#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def check(data: dict[str, Any]) -> dict[str, Any]:
    req = data.get("route_guard_requirements") or data.get("requirements") or {}
    changes = data.get("changes") or {}
    route = data.get("route") or req.get("route") or "unknown"
    violations: list[dict[str, Any]] = []

    def fail(kind: str, message: str, **extra: Any) -> None:
        row = {"type": kind, "message": message}
        row.update(extra)
        violations.append(row)

    modified_files = as_list(changes.get("modified_files"))
    added_files = as_list(changes.get("added_files"))
    max_modified = int(req.get("max_modified_files", 9999))
    max_added = int(req.get("max_added_files", 9999))

    if len(modified_files) > max_modified:
        fail(
            "modified_file_budget_exceeded",
            f"{len(modified_files)} modified files exceeds route budget {max_modified}.",
            actual=len(modified_files),
            limit=max_modified,
        )
    if len(added_files) > max_added:
        fail(
            "added_file_budget_exceeded",
            f"{len(added_files)} added files exceeds route budget {max_added}.",
            actual=len(added_files),
            limit=max_added,
        )

    boolean_checks = [
        ("dependencies_added", "allow_dependencies", "dependency_change_not_allowed", "Dependency changes are not allowed by this route."),
        ("api_contract_changed", "allow_api_changes", "api_change_not_allowed", "API contract changes are not allowed by this route."),
        ("schema_changed", "allow_schema_changes", "schema_change_not_allowed", "Schema changes are not allowed by this route."),
        ("global_style_changed", "allow_global_style_changes", "global_style_change_not_allowed", "Global style/token changes are not allowed by this route."),
        ("shared_component_changed", "allow_shared_component_changes", "shared_component_change_not_allowed", "Shared component changes are not allowed by this route."),
        ("new_components_added", "allow_new_components", "new_component_not_allowed", "New components are not allowed by this route."),
        ("rewrite_detected", "allow_rewrite", "rewrite_not_allowed", "Rewrite-level changes are not allowed by this route."),
    ]
    for actual_key, allow_key, violation_type, message in boolean_checks:
        if bool(changes.get(actual_key)) and not bool(req.get(allow_key, False)):
            fail(violation_type, message)

    if changes.get("tests_deleted"):
        fail("tests_deleted", "Tests were deleted; route guard requires explicit justification and rerouting.")
    if changes.get("assertions_weakened"):
        fail("assertions_weakened", "Assertions were weakened; route guard requires explicit justification and rerouting.")
    if changes.get("tests_skipped"):
        fail("tests_skipped", "Tests were skipped; route guard requires explicit justification and rerouting.")

    touched_shared = as_list(changes.get("shared_components_changed"))
    if touched_shared and not bool(req.get("allow_shared_component_changes", False)):
        fail("shared_components_changed", "Shared components changed under a route that forbids shared component edits.", paths=touched_shared)
    touched_global = as_list(changes.get("global_style_files_changed"))
    if touched_global and not bool(req.get("allow_global_style_changes", False)):
        fail("global_style_files_changed", "Global style/token files changed under a route that forbids global style edits.", paths=touched_global)

    recommended_route = "unchanged"
    if violations:
        if any(v["type"] in {"api_change_not_allowed", "schema_change_not_allowed", "dependency_change_not_allowed"} for v in violations):
            recommended_route = "risk_lane"
        elif any(
            v["type"]
            in {
                "shared_component_change_not_allowed",
                "shared_components_changed",
                "global_style_change_not_allowed",
                "global_style_files_changed",
                "new_component_not_allowed",
            }
            for v in violations
        ):
            recommended_route = "standard_lane"
        elif route == "micro_patch":
            recommended_route = "tiny_patch_or_standard_lane"
        else:
            recommended_route = "reroute_and_replan"

    return {
        "status": "fail" if violations else "pass",
        "route": route,
        "violations": violations,
        "required_action": "stop_and_reroute" if violations else "continue",
        "recommended_route": recommended_route,
        "summary": "Route guard failed; original route no longer matches the actual diff." if violations else "Route guard passed.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check actual changes against Project Governor route guard requirements.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = check(load(args.input))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
