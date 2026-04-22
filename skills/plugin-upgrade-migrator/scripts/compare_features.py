#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _common import load_json, version_between


def compare(matrix: dict[str, Any], current: str, target: str | None = None) -> dict[str, Any]:
    latest = target or matrix.get("current_latest") or current
    selected_versions = [version for version in matrix.get("versions", []) if version_between(str(version.get("version")), current, latest)]
    features: list[dict[str, Any]] = []

    for version in selected_versions:
        for feature in version.get("features", []):
            features.append({**feature, "version": version.get("version"), "release_title": version.get("title")})

    return {
        "current_version": current,
        "target_version": latest,
        "versions_behind": len(selected_versions),
        "new_versions": selected_versions,
        "features": features,
        "migration_required": any(feature.get("requires_project_migration") for feature in features),
        "migration_ids": sorted({feature.get("migration_id") for feature in features if feature.get("migration_id")}),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-version", required=True)
    parser.add_argument("--target-version")
    parser.add_argument("--feature-matrix", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(compare(load_json(args.feature_matrix, {}), args.current_version, args.target_version), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
