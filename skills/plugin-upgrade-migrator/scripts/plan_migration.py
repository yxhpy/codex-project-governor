#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _common import load_json, operation_policy, sha256_path, version_between, write_json

RULE_TEMPLATE_DRIFT_PATHS = ("AGENTS.md",)


def tracked(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item.get("path"): item for item in manifest.get("generated_files", []) if item.get("path")}


def migrations(plugin_root: Path, current: str, target: str) -> list[dict[str, Any]]:
    data = load_json(plugin_root / "releases" / "MIGRATIONS.json", {}) or {}
    return [migration for migration in data.get("migrations", []) if version_between(str(migration.get("to")), current, target)]


def diagnostic_operation(project: Path, plugin_root: Path, operation: dict[str, Any], relative_path: str, policy: str) -> dict[str, Any]:
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


def action_status(current_hash: str | None, source_hash: str | None, installed_hash: str | None, policy: str) -> tuple[str, str]:
    if current_hash is None:
        return ("add_if_missing", "safe_add") if source_hash else ("manual_review", "source_missing")
    if policy in {"append_only", "never_overwrite"}:
        return "skip", policy
    if installed_hash and current_hash == installed_hash:
        return "replace_from_template", "safe_update_unchanged_from_install"
    if installed_hash and current_hash != installed_hash:
        return "manual_review_or_three_way_merge", "user_modified"
    return "manual_review", "existing_untracked"


def classify(project: Path, plugin_root: Path, operation: dict[str, Any], tracked_files: dict[str, dict[str, Any]]) -> dict[str, Any]:
    relative_path = operation["path"]
    policy = operation_policy(relative_path, operation.get("upgrade_policy"))
    if operation.get("op") == "run_hygiene_check" or policy == "diagnostic_only":
        return diagnostic_operation(project, plugin_root, operation, relative_path, policy)

    current_hash = sha256_path(project / relative_path)
    source_path = operation.get("source") or relative_path
    source_hash = sha256_path(plugin_root / source_path)
    installed_hash = tracked_files.get(relative_path, {}).get("installed_sha256")
    action, status = action_status(current_hash, source_hash, installed_hash, policy)

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


def rule_template_drift_operations(
    project: Path,
    plugin_root: Path,
    tracked_files: dict[str, dict[str, Any]],
    existing_operations: list[dict[str, Any]],
    current: str,
    target: str,
) -> list[dict[str, Any]]:
    existing_paths = {operation.get("path") for operation in existing_operations}
    operations: list[dict[str, Any]] = []

    for relative_path in RULE_TEMPLATE_DRIFT_PATHS:
        if relative_path in existing_paths:
            continue

        tracked_file = tracked_files.get(relative_path)
        if not tracked_file:
            continue

        source_path = tracked_file.get("template") or f"templates/{relative_path}"
        source_hash = sha256_path(plugin_root / source_path)
        if source_hash is None:
            continue

        current_hash = sha256_path(project / relative_path)
        if current_hash == source_hash:
            continue

        installed_template_hash = tracked_file.get("template_sha256") or tracked_file.get("installed_sha256")
        if installed_template_hash == source_hash:
            continue

        operations.append(
            {
                **classify(
                    project,
                    plugin_root,
                    {
                        "op": "review_rule_template_drift",
                        "path": relative_path,
                        "source": source_path,
                        "upgrade_policy": "three_way_merge",
                        "reason": "Review updated mandatory Project Governor rules from the latest AGENTS.md template without overwriting local project rules.",
                    },
                    tracked_files,
                ),
                "migration_id": "rule_template_drift",
                "from": current,
                "to": target,
            }
        )

    return operations


def migration_operations(project: Path, plugin_root: Path, current: str, target: str, tracked_files: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
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
    return operations


def operation_groups(operations: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    safe = [operation for operation in operations if operation["action"] in {"add_if_missing", "replace_from_template"}]
    manual = [operation for operation in operations if operation["action"] in {"manual_review", "manual_review_or_three_way_merge"}]
    skipped = [operation for operation in operations if operation["action"] == "skip"]
    return safe, manual, skipped


def recommended_action(safe: list[dict[str, Any]], manual: list[dict[str, Any]]) -> str:
    if safe and manual:
        return "apply_safe_then_review_conflicts"
    if safe:
        return "apply_safe"
    return "manual_review" if manual else "no_project_migration_needed"


def plan(project: Path, plugin_root: Path, current: str, target: str) -> dict[str, Any]:
    install_manifest = load_json(project / ".project-governor" / "INSTALL_MANIFEST.json", {}) or {}
    tracked_files = tracked(install_manifest)
    operations = migration_operations(project, plugin_root, current, target, tracked_files)
    operations.extend(rule_template_drift_operations(project, plugin_root, tracked_files, operations, current, target))

    safe, manual, skipped = operation_groups(operations)
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
        "recommended_action": recommended_action(safe, manual),
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
