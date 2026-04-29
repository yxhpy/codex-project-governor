#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

PLUGIN_NAME = "codex-project-governor"
DEFAULT_REPO = "https://github.com/yxhpy/codex-project-governor.git"


def default_plugin_dir() -> Path:
    configured = os.environ.get("CODEX_PROJECT_GOVERNOR_PLUGIN_DIR")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".codex" / "plugins" / PLUGIN_NAME


def default_marketplace_path() -> Path:
    return Path.home() / ".agents" / "plugins" / "marketplace.json"


def run(command: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=check)


def git_available() -> bool:
    try:
        run(["git", "--version"])
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def git_output(args: list[str], cwd: Path, check: bool = True) -> str:
    proc = run(["git", *args], cwd=cwd, check=check)
    return proc.stdout.strip()


def is_git_checkout(path: Path) -> bool:
    if not path.exists():
        return False
    proc = run(["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"], check=False)
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def dirty_files(path: Path) -> list[str]:
    if not is_git_checkout(path):
        return []
    output = git_output(["status", "--porcelain"], cwd=path)
    return [line for line in output.splitlines() if line.strip()]


def marketplace_root(marketplace_path: Path) -> Path:
    resolved = marketplace_path.expanduser().resolve()
    if resolved.parent.name == "plugins" and resolved.parent.parent.name == ".agents":
        return resolved.parent.parent.parent
    return resolved.parent


def local_source_path(plugin_dir: Path, marketplace_path: Path) -> str:
    root = marketplace_root(marketplace_path)
    try:
        rel = os.path.relpath(plugin_dir.expanduser().resolve(), root)
    except ValueError:
        return str(plugin_dir.expanduser().resolve())
    if rel == ".":
        return "."
    if rel.startswith(".."):
        return str(plugin_dir.expanduser().resolve())
    return "./" + rel.replace(os.sep, "/")


def load_marketplace(path: Path) -> dict:
    if not path.exists():
        return {
            "name": "personal-codex-plugins",
            "interface": {"displayName": "Personal Codex Plugins"},
            "plugins": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def upsert_marketplace_entry(marketplace: dict, plugin_dir: Path, marketplace_path: Path) -> tuple[dict, dict]:
    marketplace.setdefault("name", "personal-codex-plugins")
    marketplace.setdefault("interface", {}).setdefault("displayName", "Personal Codex Plugins")
    plugins = marketplace.setdefault("plugins", [])
    entry = {
        "name": PLUGIN_NAME,
        "source": {
            "source": "local",
            "path": local_source_path(plugin_dir, marketplace_path),
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": "Developer Tools",
    }
    for index, existing in enumerate(plugins):
        if existing.get("name") == PLUGIN_NAME:
            plugins[index] = entry
            return marketplace, entry
    plugins.append(entry)
    return marketplace, entry


def current_version(plugin_dir: Path) -> str | None:
    manifest = plugin_dir / ".codex-plugin" / "plugin.json"
    if not manifest.exists():
        return None
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    value = data.get("version")
    return value if isinstance(value, str) else None


def checkout_ref(plugin_dir: Path, ref: str) -> list[dict]:
    operations: list[dict] = []
    git_output(["fetch", "--tags", "origin"], cwd=plugin_dir)
    operations.append({"op": "git_fetch", "status": "applied"})

    if ref in {"", "HEAD"}:
        default_ref = git_output(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=plugin_dir, check=False)
        branch = default_ref.removeprefix("origin/") if default_ref.startswith("origin/") else "main"
        git_output(["checkout", branch], cwd=plugin_dir)
        git_output(["pull", "--ff-only", "origin", branch], cwd=plugin_dir)
        operations.append({"op": "git_pull", "status": "applied", "ref": branch})
        return operations

    if ref == "main":
        git_output(["checkout", "main"], cwd=plugin_dir)
        git_output(["pull", "--ff-only", "origin", "main"], cwd=plugin_dir)
        operations.append({"op": "git_pull", "status": "applied", "ref": "main"})
        return operations

    git_output(["checkout", "--detach", ref], cwd=plugin_dir)
    operations.append({"op": "git_checkout", "status": "applied", "ref": ref})
    return operations


def build_plan(plugin_dir: Path, marketplace_path: Path, repo_url: str, ref: str, run_selftest: bool) -> dict:
    entry_path = local_source_path(plugin_dir, marketplace_path)
    operations = []
    if not plugin_dir.exists():
        operations.append({"op": "git_clone", "path": str(plugin_dir), "repo_url": repo_url})
    elif is_git_checkout(plugin_dir):
        operations.append({"op": "git_fetch_checkout", "path": str(plugin_dir), "ref": ref})
    else:
        operations.append({"op": "blocked_non_git_checkout", "path": str(plugin_dir)})
    operations.append({"op": "write_marketplace_entry", "path": str(marketplace_path), "source_path": entry_path})
    if run_selftest:
        operations.append({"op": "run_selftest", "path": str(plugin_dir / "tests" / "selftest.py")})
    return {
        "status": "planned",
        "plugin_dir": str(plugin_dir),
        "marketplace_path": str(marketplace_path),
        "repo_url": repo_url,
        "ref": ref,
        "current_version": current_version(plugin_dir),
        "target_source": {"source": "local", "path": entry_path},
        "operations": operations,
        "notes": [
            "This updates the local Git checkout that the Codex marketplace points at.",
            "The Codex marketplace entry remains local; built-in Git marketplace upgrades do not fetch this checkout.",
            "Run with --apply to write files.",
        ],
    }


def apply(plugin_dir: Path, marketplace_path: Path, repo_url: str, ref: str, run_selftest: bool) -> dict:
    if not git_available():
        return {"status": "blocked", "reason": "git_not_found", "plugin_dir": str(plugin_dir)}

    operations: list[dict] = []
    before = current_version(plugin_dir)

    if plugin_dir.exists() and not is_git_checkout(plugin_dir):
        return {
            "status": "blocked",
            "reason": "plugin_dir_not_git_checkout",
            "plugin_dir": str(plugin_dir),
            "notes": ["Move the directory aside or choose a different --plugin-dir before applying."],
        }

    if is_git_checkout(plugin_dir):
        dirty = dirty_files(plugin_dir)
        if dirty:
            return {
                "status": "blocked",
                "reason": "dirty_plugin_checkout",
                "plugin_dir": str(plugin_dir),
                "dirty_files": dirty,
                "notes": ["Commit, stash, or move local plugin edits before applying an update."],
            }
        operations.extend(checkout_ref(plugin_dir, ref))
    else:
        plugin_dir.parent.mkdir(parents=True, exist_ok=True)
        git_output(["clone", repo_url, str(plugin_dir)], cwd=plugin_dir.parent)
        operations.append({"op": "git_clone", "status": "applied", "repo_url": repo_url})
        operations.extend(checkout_ref(plugin_dir, ref))

    marketplace_path.parent.mkdir(parents=True, exist_ok=True)
    marketplace = load_marketplace(marketplace_path)
    marketplace, entry = upsert_marketplace_entry(marketplace, plugin_dir, marketplace_path)
    marketplace_path.write_text(json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    operations.append({"op": "write_marketplace_entry", "status": "applied", "path": str(marketplace_path)})

    selftest = plugin_dir / "tests" / "selftest.py"
    selftest_status = "skipped"
    if run_selftest and selftest.exists():
        proc = run([sys.executable, str(selftest)], cwd=plugin_dir, check=False)
        selftest_status = "passed" if proc.returncode == 0 else "failed"
        operations.append({
            "op": "run_selftest",
            "status": selftest_status,
            "returncode": proc.returncode,
        })

    status = "applied" if selftest_status != "failed" else "applied_with_selftest_failure"
    return {
        "status": status,
        "plugin_dir": str(plugin_dir),
        "marketplace_path": str(marketplace_path),
        "repo_url": repo_url,
        "ref": ref,
        "previous_version": before,
        "current_version": current_version(plugin_dir),
        "marketplace_entry": entry,
        "operations": operations,
        "next_steps": [
            "Restart Codex so the plugin catalog reloads.",
            "Use plugin-upgrade-migrator inside initialized projects when governance files need migration.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Install or update the user-level Project Governor plugin checkout and local marketplace entry.")
    parser.add_argument("--plugin-dir", type=Path, default=default_plugin_dir())
    parser.add_argument("--marketplace-path", type=Path, default=default_marketplace_path())
    parser.add_argument("--repo-url", default=DEFAULT_REPO)
    parser.add_argument("--ref", default="main")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--skip-selftest", action="store_true")
    args = parser.parse_args()

    plugin_dir = args.plugin_dir.expanduser().resolve()
    marketplace_path = args.marketplace_path.expanduser().resolve()
    run_selftest = not args.skip_selftest

    if args.apply:
        result = apply(plugin_dir, marketplace_path, args.repo_url, args.ref, run_selftest)
    else:
        result = build_plan(plugin_dir, marketplace_path, args.repo_url, args.ref, run_selftest)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] in {"blocked", "applied_with_selftest_failure"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
