#!/usr/bin/env python3
"""Initialize Project Governor governance files in a target repository.

This script copies templates into a target repository and preserves existing
files by default. It never edits application directories directly; it only writes
files from the plugin's templates directory.
"""
from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass, asdict
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


@dataclass
class InitResult:
    mode: str
    target: str
    created: list[str]
    preserved: list[str]
    skipped: list[str]


def iter_template_files() -> list[Path]:
    return sorted(path for path in TEMPLATE_ROOT.rglob("*") if path.is_file())


def is_application_path(rel: Path) -> bool:
    text = rel.as_posix()
    return text.startswith(APP_PREFIXES) or rel.name in PACKAGE_FILES


def copy_templates(target: Path, *, mode: str, overwrite: bool = False) -> InitResult:
    if not TEMPLATE_ROOT.exists():
        raise FileNotFoundError(f"Template root not found: {TEMPLATE_ROOT}")

    created: list[str] = []
    preserved: list[str] = []
    skipped: list[str] = []

    for src in iter_template_files():
        rel = src.relative_to(TEMPLATE_ROOT)
        if is_application_path(rel):
            skipped.append(rel.as_posix())
            continue

        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not overwrite:
            preserved.append(rel.as_posix())
            continue
        shutil.copy2(src, dst)
        created.append(rel.as_posix())

    return InitResult(mode=mode, target=str(target), created=created, preserved=preserved, skipped=skipped)


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize Codex Project Governor governance files.")
    parser.add_argument("--mode", choices=["empty", "existing"], default="existing")
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing governance files. Use with care.")
    parser.add_argument("--json", action="store_true", help="Print JSON only.")
    args = parser.parse_args()

    target = args.target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    result = copy_templates(target, mode=args.mode, overwrite=args.overwrite)

    report_dir = target / "reports" / "project-governor"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = report_dir / "init-report.json"
    report.write_text(json.dumps(asdict(result), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    else:
        print(f"Project Governor initialized {target}")
        print(f"Created: {len(result.created)}")
        print(f"Preserved: {len(result.preserved)}")
        print(f"Skipped: {len(result.skipped)}")
        print(f"Report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
