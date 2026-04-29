#!/usr/bin/env python3
"""Initialize Project Governor governance files in a target repository.

This script copies templates into a target repository and preserves existing
files by default. It never edits application directories directly; it only writes
files from the plugin's templates directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PLUGIN_ROOT / "templates"

APP_PREFIXES = ("src/", "app/", "apps/", "packages/", "services/", "lib/")
PACKAGE_FILES = {
    "package.json",
    "pnpm-lock.yaml",
    "package-lock.json",
    "yarn.lock",
    "bun.lockb",
    "pyproject.toml",
    "requirements.txt",
    "poetry.lock",
    "uv.lock",
    "Cargo.toml",
    "go.mod",
}
GLOBAL_TEMPLATE_PREFIXES = (".codex/agents/", ".codex/prompts/")
GLOBAL_TEMPLATE_FILES = {".codex/config.toml"}
PROJECT_LOCAL_PREFIXES = ("docs/", "tasks/_template/", ".project-governor/", ".codex/rules/", ".codex/hooks/")
PROJECT_LOCAL_FILES = {"AGENTS.md", "CLAUDE.md", ".codex/hooks.json"}


@dataclass
class InitResult:
    mode: str
    profile: str
    target: str
    created: list[str]
    preserved: list[str]
    skipped: list[str]
    skipped_application: list[str]
    skipped_global: list[str]
    install_manifest: str | None


def sha256_path(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def plugin_version() -> str:
    try:
        manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        return str(manifest.get("version", "unknown"))
    except (OSError, json.JSONDecodeError):
        return "unknown"


def iter_template_files() -> list[Path]:
    return sorted(path for path in TEMPLATE_ROOT.rglob("*") if path.is_file())


def is_application_path(rel: Path) -> bool:
    text = rel.as_posix()
    return text.startswith(APP_PREFIXES) or rel.name in PACKAGE_FILES


def is_global_template(rel: Path) -> bool:
    text = rel.as_posix()
    return text in GLOBAL_TEMPLATE_FILES or any(text.startswith(prefix) for prefix in GLOBAL_TEMPLATE_PREFIXES)


def is_project_local_template(rel: Path) -> bool:
    text = rel.as_posix()
    return text in PROJECT_LOCAL_FILES or any(text.startswith(prefix) for prefix in PROJECT_LOCAL_PREFIXES)


def template_policy(rel: str) -> str:
    if rel.startswith("docs/memory/"):
        return "append_only"
    if rel.startswith("docs/decisions/"):
        return "never_overwrite"
    if rel == "AGENTS.md" or rel.startswith("docs/conventions/"):
        return "three_way_merge"
    return "add_if_missing"


def write_install_manifest(
    target: Path,
    *,
    created: list[str],
    preserved: list[str],
    profile: str,
    overwrite: bool,
) -> str:
    manifest_path = target / ".project-governor" / "INSTALL_MANIFEST.json"
    manifest_rel = manifest_path.relative_to(target).as_posix()
    if manifest_rel in preserved and not overwrite:
        return manifest_rel

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    generated_files: list[dict[str, str | None]] = []
    for rel in sorted(set(created + preserved)):
        if rel == manifest_rel:
            continue
        source = TEMPLATE_ROOT / rel
        destination = target / rel
        if not source.exists() or not destination.exists():
            continue
        generated_files.append(
            {
                "path": rel,
                "template": f"templates/{rel}",
                "template_version": plugin_version(),
                "template_sha256": sha256_path(source),
                "installed_sha256": sha256_path(destination),
                "upgrade_policy": template_policy(rel),
            }
        )

    manifest = {
        "plugin": {
            "name": "codex-project-governor",
            "installed_version": plugin_version(),
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "source": str(PLUGIN_ROOT),
        },
        "init_profile": profile,
        "generated_files": generated_files,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest_rel


def template_skip_reason(rel: Path, profile: str, include_global: bool) -> str | None:
    if is_application_path(rel):
        return "application"
    if is_global_template(rel) and not include_global:
        return "global"
    if profile == "clean" and not is_project_local_template(rel) and not is_global_template(rel):
        return "global"
    return None


def copy_template_file(src: Path, target: Path, rel: Path, overwrite: bool) -> str:
    dst = target / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        return "preserved"
    shutil.copy2(src, dst)
    return "created"


def copy_templates(target: Path, *, mode: str, profile: str = "clean", overwrite: bool = False) -> InitResult:
    if not TEMPLATE_ROOT.exists():
        raise FileNotFoundError(f"Template root not found: {TEMPLATE_ROOT}")

    created: list[str] = []
    preserved: list[str] = []
    skipped_application: list[str] = []
    skipped_global: list[str] = []
    include_global = profile == "legacy-full"

    for src in iter_template_files():
        rel = src.relative_to(TEMPLATE_ROOT)
        text = rel.as_posix()
        skip_reason = template_skip_reason(rel, profile, include_global)
        if skip_reason == "application":
            skipped_application.append(text)
            continue
        if skip_reason == "global":
            skipped_global.append(text)
            continue

        status = copy_template_file(src, target, rel, overwrite)
        if status == "preserved":
            preserved.append(text)
        else:
            created.append(text)

    manifest_rel = write_install_manifest(
        target,
        created=created,
        preserved=preserved,
        profile=profile,
        overwrite=overwrite,
    )
    if manifest_rel not in created and manifest_rel not in preserved:
        created.append(manifest_rel)

    skipped = skipped_application + skipped_global
    return InitResult(
        mode=mode,
        profile=profile,
        target=str(target),
        created=created,
        preserved=preserved,
        skipped=skipped,
        skipped_application=skipped_application,
        skipped_global=skipped_global,
        install_manifest=manifest_rel,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize Codex Project Governor governance files.")
    parser.add_argument("--mode", choices=["empty", "existing"], default="existing")
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument(
        "--profile",
        choices=["clean", "legacy-full"],
        default="clean",
        help="clean copies project-owned governance files only; legacy-full also copies bundled .codex runtime assets.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing governance files. Use with care.")
    parser.add_argument("--json", action="store_true", help="Print JSON only.")
    args = parser.parse_args()

    target = args.target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    result = copy_templates(target, mode=args.mode, profile=args.profile, overwrite=args.overwrite)

    report_dir = target / "reports" / "project-governor"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = report_dir / "init-report.json"
    report.write_text(json.dumps(asdict(result), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    else:
        print(f"Project Governor initialized {target}")
        print(f"Profile: {result.profile}")
        print(f"Created: {len(result.created)}")
        print(f"Preserved: {len(result.preserved)}")
        print(f"Skipped application: {len(result.skipped_application)}")
        print(f"Skipped plugin/global templates: {len(result.skipped_global)}")
        print(f"Install manifest: {result.install_manifest}")
        print(f"Report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
