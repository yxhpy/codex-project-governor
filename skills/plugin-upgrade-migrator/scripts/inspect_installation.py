#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _common import load_json, sha256_path


def file_status(current_hash: str | None, installed_hash: str | None) -> str:
    if current_hash is None:
        return "missing"
    if installed_hash and current_hash == installed_hash:
        return "unchanged_from_install"
    if installed_hash:
        return "user_modified"
    return "tracked_unknown_hash"


def inspect(project: Path) -> dict[str, Any]:
    manifest_path = project / ".project-governor" / "INSTALL_MANIFEST.json"
    manifest = load_json(manifest_path, {}) or {}
    files: list[dict[str, Any]] = []

    for item in manifest.get("generated_files", []):
        relative_path = item.get("path")
        if not relative_path:
            continue
        current_hash = sha256_path(project / relative_path)
        installed_hash = item.get("installed_sha256")
        files.append({**item, "current_sha256": current_hash, "status": file_status(current_hash, installed_hash)})

    return {
        "status": "manifest_missing" if not manifest else "installed",
        "project": str(project),
        "installed_version": manifest.get("plugin", {}).get("installed_version"),
        "tracked_files": files,
        "summary": {
            "tracked_count": len(files),
            "user_modified_count": sum(item["status"] == "user_modified" for item in files),
            "missing_count": sum(item["status"] == "missing" for item in files),
            "unchanged_count": sum(item["status"] == "unchanged_from_install" for item in files),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(inspect(args.project), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
