#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _common import load_json, operation_policy, sha256_path, version_between, write_json


def tracked(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item.get("path"): item for item in manifest.get("generated_files", []) if item.get("path")}


def migrations(plugin_root: Path, current: str, target: str) -> list[dict[str, Any]]:
    data = load_json(plugin_root / "releases" / "MIGRATIONS.json", {}) or {}
    return [migration for migration in data.get("migrations", []) if version_between(str(migration.get("to")), current, target)]


def classify(project: Path, plugin_root: Path, operation: dict[str, Any], tracked_files: dict[str, dict[str, Any]]) -> dict[str, Any]:
    relative_path = operation["path"]
    policy = operation_policy(relative_path, operation.get("upgrade_policy"))
    if operation.get("op") == "run_hygiene_check" or policy == "diagnostic_only":
        return {
            "op": operation.get("op", "diagnostic"),
            "path": relative_path,
            "source": operation.get("source"),
            "policy": policy,
            "status": "diagnostic_only",
            "action": "manual_review",
            "project_exists": project.exists(),
            "current_sha256": None,
            "installed_sha256": None,
            "source_sha256": sha256_path(plugin_root / operation.get("source", "")) if operation.get("source") else None,
            "reason": operation.get("reason", ""),
        }

    current_hash = sha256_path(project / relative_path)
    source_path = operation.get("source") or relative_path
    source_hash = sha256_path(plugin_root / source_path)
    installed_hash = tracked_files.get(relative_path, {}).get("installed_sha256")

    if current_hash is None:
        action = "add_if_missing" if source_hash else "manual_review"
        status = "safe_add" if source_hash else "source_missing"
    elif policy in {"append_only", "never_overwrite"}:
        action = "skip"
        status = policy
    elif installed_hash and current_hash == installed_hash:
        action = "replace_from_template"
        status = "safe_update_unchanged_from_install"
    elif installed_hash and current_hash != installed_hash:
        action = "manual_review_or_three_way_merge"
        status = "user_modified"
    else:
        action = "manual_review"
        status = "existing_untracked"

    return {
        "op": operation.get("op", "add_or_merge"),
        "path": relative_path,
        "source": source_path,
        "policy": policy,
        "status": status,
        "action": action,
        "project_exists": current_hash is not None,
        "current_sha256": current_hash,
        "installed_sha256": installed_hash,
        "source_sha256": source_hash,
        "reason": operation.get("reason", ""),
    }


def plan(project: Path, plugin_root: Path, current: str, target: str) -> dict[str, Any]:
    install_manifest = load_json(project / ".project-governor" / "INSTALL_MANIFEST.json", {}) or {}
    tracked_files = tracked(install_manifest)
    operations: list[dict[str, Any]] = []

    for migration in migrations(plugin_root, current, target):
        for operation in migration.get("operations", []):
            operations.append(
                {
                    **classify(project, plugin_root, operation, tracked_files),
                    "migration_id": migration.get("id"),
                    "from": migration.get("from"),
                    "to": migration.get("to"),
                }
            )

    safe = [operation for operation in operations if operation["action"] in {"add_if_missing", "replace_from_template"}]
    manual = [operation for operation in operations if operation["action"] in {"manual_review", "manual_review_or_three_way_merge"}]
    skipped = [operation for operation in operations if operation["action"] == "skip"]
    return {
        "status": "planned",
        "project": str(project),
        "plugin_root": str(plugin_root),
        "current_version": current,
        "target_version": target,
        "operations": operations,
        "summary": {
            "operation_count": len(operations),
            "safe_operation_count": len(safe),
            "manual_review_count": len(manual),
            "skipped_count": len(skipped),
        },
        "recommended_action": "apply_safe_then_review_conflicts"
        if safe and manual
        else ("apply_safe" if safe else ("manual_review" if manual else "no_project_migration_needed")),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--plugin-root", type=Path, required=True)
    parser.add_argument("--current-version", required=True)
    parser.add_argument("--target-version", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = plan(args.project, args.plugin_root, args.current_version, args.target_version)
    if args.output:
        write_json(args.output, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
