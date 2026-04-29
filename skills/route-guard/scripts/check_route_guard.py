#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

COLLECT_DIFF = Path(__file__).resolve().with_name("collect_diff_facts.py")
BOOLEAN_CHECKS = [
    ("dependencies_added", "allow_dependencies", "dependency_change_not_allowed", "Dependency changes are not allowed by this route."),
    ("api_contract_changed", "allow_api_changes", "api_change_not_allowed", "API contract changes are not allowed by this route."),
    ("schema_changed", "allow_schema_changes", "schema_change_not_allowed", "Schema changes are not allowed by this route."),
    ("global_style_changed", "allow_global_style_changes", "global_style_change_not_allowed", "Global style/token changes are not allowed by this route."),
    ("shared_component_changed", "allow_shared_component_changes", "shared_component_change_not_allowed", "Shared component changes are not allowed by this route."),
    ("new_components_added", "allow_new_components", "new_component_not_allowed", "New components are not allowed by this route."),
    ("rewrite_detected", "allow_rewrite", "rewrite_not_allowed", "Rewrite-level changes are not allowed by this route."),
]
TEST_POLICY_CHECKS = [
    ("tests_deleted", "tests_deleted", "Tests were deleted; route guard requires explicit justification and rerouting."),
    ("assertions_weakened", "assertions_weakened", "Assertions were weakened; route guard requires explicit justification and rerouting."),
    ("tests_skipped", "tests_skipped", "Tests were skipped or weakened; route guard requires explicit justification and rerouting."),
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def collect_changes(repo: Path) -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("project_governor_collect_diff_facts", COLLECT_DIFF)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {COLLECT_DIFF}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.collect(repo)


def add_violation(violations: list[dict[str, Any]], kind: str, message: str, **extra: Any) -> None:
    row = {"type": kind, "message": message}
    row.update(extra)
    violations.append(row)


def changes_from(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("collect_diff") or data.get("repo"):
        return collect_changes(Path(data.get("repo", ".")).resolve())
    return data.get("changes") or {}


def file_budget_violations(req: dict[str, Any], changes: dict[str, Any]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    modified_files = as_list(changes.get("modified_files"))
    added_files = as_list(changes.get("added_files"))
    max_modified = int(req.get("max_modified_files", 9999))
    max_added = int(req.get("max_added_files", 9999))
    if len(modified_files) > max_modified:
        add_violation(violations, "modified_file_budget_exceeded", f"{len(modified_files)} modified files exceeds route budget {max_modified}.", actual=len(modified_files), limit=max_modified, paths=modified_files)
    if len(added_files) > max_added:
        add_violation(violations, "added_file_budget_exceeded", f"{len(added_files)} added files exceeds route budget {max_added}.", actual=len(added_files), limit=max_added, paths=added_files)
    return violations


def boolean_violations(req: dict[str, Any], changes: dict[str, Any]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for actual_key, allow_key, violation_type, message in BOOLEAN_CHECKS:
        if bool(changes.get(actual_key)) and not bool(req.get(allow_key, False)):
            add_violation(violations, violation_type, message)
    return violations


def test_policy_violations(changes: dict[str, Any]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for change_key, violation_type, message in TEST_POLICY_CHECKS:
        if changes.get(change_key):
            add_violation(violations, violation_type, message)
    return violations


def touched_path_violations(req: dict[str, Any], changes: dict[str, Any]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    touched_shared = as_list(changes.get("shared_components_changed"))
    if touched_shared and not bool(req.get("allow_shared_component_changes", False)):
        add_violation(violations, "shared_components_changed", "Shared components changed under a route that forbids shared component edits.", paths=touched_shared)
    touched_global = as_list(changes.get("global_style_files_changed"))
    if touched_global and not bool(req.get("allow_global_style_changes", False)):
        add_violation(violations, "global_style_files_changed", "Global style/token files changed under a route that forbids global style edits.", paths=touched_global)
    return violations


def recommended_route_for(violations: list[dict[str, Any]], route: str) -> str:
    if not violations:
        return "unchanged"
    violation_types = {v["type"] for v in violations}
    if violation_types & {"api_change_not_allowed", "schema_change_not_allowed", "dependency_change_not_allowed"}:
        return "risk_lane"
    if violation_types & {"shared_component_change_not_allowed", "shared_components_changed", "global_style_change_not_allowed", "global_style_files_changed", "new_component_not_allowed"}:
        return "standard_lane"
    if route == "micro_patch":
        return "tiny_patch_or_standard_lane"
    return "reroute_and_replan"


def result_for(route: str, changes: dict[str, Any], violations: list[dict[str, Any]]) -> dict[str, Any]:
    failed = bool(violations)
    return {
        "status": "fail" if failed else "pass",
        "schema": "project-governor-route-guard-v2",
        "route": route,
        "violations": violations,
        "changes": changes,
        "required_action": "stop_and_reroute" if failed else "continue",
        "recommended_route": recommended_route_for(violations, route),
        "summary": "Route guard failed; original route no longer matches the actual diff." if failed else "Route guard passed.",
    }


def check(data: dict[str, Any]) -> dict[str, Any]:
    req = data.get("route_guard_requirements") or data.get("requirements") or {}
    changes = changes_from(data)
    route = data.get("route") or req.get("route") or "unknown"
    violations: list[dict[str, Any]] = []
    violations.extend(file_budget_violations(req, changes))
    violations.extend(boolean_violations(req, changes))
    violations.extend(test_policy_violations(changes))
    violations.extend(touched_path_violations(req, changes))
    return result_for(route, changes, violations)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check actual changes against Project Governor route guard requirements.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = check(load(args.input))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
