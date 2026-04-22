#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PLUGIN_SOURCE_PREFIXES = (".codex-plugin/", "skills/", "templates/", "releases/")
GLOBAL_CODEX_PREFIXES = (".codex/agents/", ".codex/prompts/")
GLOBAL_CODEX_FILES = {".codex/config.toml"}
PROJECT_OWNED_PREFIXES = ("docs/", "tasks/_template/", ".project-governor/", ".codex/rules/", ".codex/hooks/")
PROJECT_OWNED_FILES = {"AGENTS.md", ".codex/hooks.json"}
NEVER_TOUCH_PREFIXES = ("docs/memory/", "docs/decisions/")
IGNORED_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "coverage"}


@dataclass
class Finding:
    path: str
    classification: str
    status: str
    action: str
    reason: str
    current_sha256: str | None = None
    installed_sha256: str | None = None
    policy: str | None = None


def sha256_path(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def is_plugin_repo(project: Path, plugin_root: Path | None = None) -> bool:
    if plugin_root:
        return project.resolve() == plugin_root.resolve()
    return load_json(project / ".codex-plugin" / "plugin.json").get("name") == "codex-project-governor"


def iter_files(project: Path) -> list[Path]:
    paths: list[Path] = []
    for path in sorted(project.rglob("*")):
        if not path.is_file():
            continue
        if set(path.relative_to(project).parts) & IGNORED_DIRS:
            continue
        paths.append(path)
    return paths


def tracked_files(project: Path) -> dict[str, dict[str, Any]]:
    manifest = load_json(project / ".project-governor" / "INSTALL_MANIFEST.json")
    return {str(item.get("path")): item for item in manifest.get("generated_files", []) if item.get("path")}


def has_prefix(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def classify(project: Path, rel: str, tracked: dict[str, dict[str, Any]], plugin_repo: bool) -> Finding | None:
    path = project / rel
    current_hash = sha256_path(path)
    tracked_item = tracked.get(rel, {})
    installed_hash = tracked_item.get("installed_sha256") or tracked_item.get("template_sha256")
    policy = tracked_item.get("upgrade_policy")

    if has_prefix(rel, NEVER_TOUCH_PREFIXES):
        return Finding(
            rel,
            "project_memory_or_decision",
            "protected",
            "never_touch",
            "Memory and decision files are project-owned and must not be removed by hygiene cleanup.",
            current_hash,
            installed_hash,
            policy,
        )

    if rel in PROJECT_OWNED_FILES or has_prefix(rel, PROJECT_OWNED_PREFIXES):
        return Finding(
            rel,
            "project_owned",
            "ok",
            "keep",
            "Project-owned governance file.",
            current_hash,
            installed_hash,
            policy,
        )

    if plugin_repo and has_prefix(rel, PLUGIN_SOURCE_PREFIXES):
        return Finding(
            rel,
            "plugin_repo_source",
            "ok",
            "keep",
            "This directory appears to be the Project Governor plugin repository itself.",
            current_hash,
            installed_hash,
            policy,
        )

    if plugin_repo and (has_prefix(rel, GLOBAL_CODEX_PREFIXES) or rel in GLOBAL_CODEX_FILES):
        return Finding(
            rel,
            "plugin_repo_runtime_asset",
            "ok",
            "keep",
            "This .codex runtime asset belongs to the Project Governor plugin repository itself.",
            current_hash,
            installed_hash,
            policy,
        )

    if has_prefix(rel, PLUGIN_SOURCE_PREFIXES):
        return Finding(
            rel,
            "plugin_source_leak",
            "manual_review",
            "review_remove_or_move",
            "Project Governor plugin source-like file found in a non-plugin target project.",
            current_hash,
            installed_hash,
            policy,
        )

    if has_prefix(rel, GLOBAL_CODEX_PREFIXES) or rel in GLOBAL_CODEX_FILES:
        if installed_hash and current_hash and installed_hash == current_hash:
            return Finding(
                rel,
                "generated_global_codex_asset",
                "safe_to_quarantine",
                "quarantine",
                "Generated global Codex asset is unchanged from install manifest; keep it in the plugin, not the project.",
                current_hash,
                installed_hash,
                policy,
            )
        if tracked_item and current_hash and installed_hash and current_hash != installed_hash:
            return Finding(
                rel,
                "modified_global_codex_asset",
                "manual_review",
                "keep_and_review",
                "Generated global Codex asset was modified; treat it as a possible project override.",
                current_hash,
                installed_hash,
                policy,
            )
        return Finding(
            rel,
            "untracked_global_codex_asset",
            "manual_review",
            "keep_and_review",
            "Untracked .codex runtime asset may be a project override.",
            current_hash,
            installed_hash,
            policy,
        )

    return None


def quarantine(project: Path, rel: str, quarantine_root: Path) -> str:
    destination = quarantine_root / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(project / rel), str(destination))
    return destination.relative_to(project).as_posix()


def recommendation(status: str, safe: list[Finding], manual: list[Finding]) -> str:
    if status == "clean":
        return "Project hygiene is clean. Run plugin-upgrade-migrator normally."
    if safe and not manual:
        return "Run with --apply to quarantine generated global assets, then run plugin-upgrade-migrator."
    if safe and manual:
        return "Run with --apply to quarantine safe generated assets; review custom or untracked global assets manually."
    return "Review untracked plugin/global-looking files before running migrations."


def inspect(project: Path, plugin_root: Path | None = None, apply_changes: bool = False) -> dict[str, Any]:
    project = project.resolve()
    tracked = tracked_files(project)
    plugin_repo = is_plugin_repo(project, plugin_root)
    findings = [
        finding
        for path in iter_files(project)
        if (finding := classify(project, path.relative_to(project).as_posix(), tracked, plugin_repo))
    ]
    safe = [finding for finding in findings if finding.action == "quarantine"]
    manual = [finding for finding in findings if finding.status == "manual_review"]
    protected = [finding for finding in findings if finding.action == "never_touch"]

    applied: list[dict[str, str]] = []
    quarantine_root = project / ".project-governor" / "hygiene-quarantine" / datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )
    if apply_changes:
        for finding in safe:
            applied.append({"path": finding.path, "quarantined_to": quarantine(project, finding.path, quarantine_root)})

    status = "clean"
    if manual:
        status = "needs_manual_review"
    if safe:
        status = "needs_cleanup" if not apply_changes else "clean_after_quarantine"
        if manual and apply_changes:
            status = "needs_manual_review_after_safe_quarantine"

    return {
        "status": status,
        "project": str(project),
        "plugin_root": str(plugin_root.resolve()) if plugin_root else None,
        "is_plugin_repo": plugin_repo,
        "summary": {
            "finding_count": len(findings),
            "safe_to_quarantine_count": len(safe),
            "manual_review_count": len(manual),
            "protected_count": len(protected),
            "applied_count": len(applied),
        },
        "findings": [asdict(finding) for finding in findings],
        "applied": applied,
        "recommendation": recommendation(status, safe, manual),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--plugin-root", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    result = inspect(args.project, args.plugin_root, args.apply)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] in {"clean", "clean_after_quarantine"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
