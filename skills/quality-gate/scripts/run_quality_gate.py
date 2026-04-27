#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

LEVELS = {"light", "standard", "strict"}
ROOT = Path(__file__).resolve().parents[3]
ROUTE_GUARD = ROOT / "skills" / "route-guard" / "scripts" / "check_route_guard.py"


def normalize_level(value: object) -> str:
    return value if isinstance(value, str) and value in LEVELS else "standard"


def check_status(value: object) -> object:
    return value.get("status") if isinstance(value, dict) else value


def load_route_guard_module() -> Any:
    spec = importlib.util.spec_from_file_location("project_governor_route_guard", ROUTE_GUARD)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {ROUTE_GUARD}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_route_guard(route_guard_payload: dict[str, Any]) -> dict[str, Any]:
    module = load_route_guard_module()
    return module.check(route_guard_payload)


def iter_checks(checks: object) -> list[tuple[str, object, str, bool, str]]:
    if isinstance(checks, dict):
        return [(str(name), check_status(result), "blocking", False, "Check failed.") for name, result in checks.items()]
    if isinstance(checks, list):
        rows = []
        for index, check in enumerate(checks):
            if isinstance(check, dict):
                rows.append((str(check.get("name", f"check_{index}")), check.get("status", "unknown"), str(check.get("severity", "blocking")), bool(check.get("required", False)), str(check.get("message", "Check failed."))))
            else:
                rows.append((f"check_{index}", check_status(check), "blocking", False, "Check failed."))
        return rows
    return []


def load_evidence(data: dict[str, Any]) -> dict[str, Any] | None:
    evidence = data.get("evidence")
    if isinstance(evidence, dict):
        return evidence
    path = data.get("evidence_manifest") or data.get("evidence_path")
    if path:
        p = Path(path)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return None


def validate_evidence(evidence: dict[str, Any] | None, required: bool, level: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if evidence is None:
        if required or level == "strict":
            findings.append({"severity": "blocking", "type": "evidence_manifest_missing", "message": "Harness v6 requires an evidence manifest for this gate."})
        return findings
    criteria = evidence.get("acceptance_criteria", [])
    tests = evidence.get("tests", [])
    if required and not criteria:
        findings.append({"severity": "blocking", "type": "acceptance_mapping_missing", "message": "Evidence manifest has no acceptance criteria mapping."})
    for index, item in enumerate(criteria):
        if not isinstance(item, dict) or not item.get("criterion") or not item.get("proof"):
            findings.append({"severity": "blocking", "type": "acceptance_mapping_incomplete", "index": index})
    if level in {"standard", "strict"} and required and not tests:
        findings.append({"severity": "blocking", "type": "evidence_tests_missing", "message": "Evidence manifest has no test or verification command records."})
    for index, item in enumerate(tests):
        if not isinstance(item, dict) or not item.get("command") or item.get("status") not in {"passed", "pass", True}:
            findings.append({"severity": "blocking", "type": "evidence_test_not_passing", "index": index, "command": item.get("command") if isinstance(item, dict) else None})
    docs_refresh = evidence.get("docs_refresh", {})
    if isinstance(docs_refresh, dict) and docs_refresh.get("needed") is True and not docs_refresh.get("files_updated"):
        findings.append({"severity": "blocking", "type": "docs_refresh_missing", "message": "Docs refresh was marked needed but no updated files were recorded."})
    return findings


def evaluate(data: dict[str, Any]) -> dict[str, Any]:
    level = normalize_level(data.get("level", data.get("quality_level", "standard")))
    findings: list[dict[str, Any]] = []
    budget = data.get("change_budget", {})
    actual = data.get("actual", {})
    checks = data.get("checks", {})
    route_guard_result = None
    route = data.get("route", data.get("task_route", ""))
    docs_only = bool(data.get("docs_only") or route == "docs_only")
    require_evidence = bool(data.get("require_evidence") or data.get("evidence_required") or level == "strict")
    require_commands = bool(data.get("require_commands") or (level in {"standard", "strict"} and not docs_only and not data.get("allow_no_commands")))

    if actual.get("files_changed", 0) > budget.get("max_files_changed", 10):
        findings.append({"severity": "blocking", "type": "change_budget_exceeded", "metric": "files_changed"})
    if actual.get("new_files", 0) > budget.get("max_new_files", 3):
        findings.append({"severity": "blocking", "type": "new_file_budget_exceeded", "metric": "new_files"})
    if actual.get("dependencies_added", 0) and not budget.get("allow_dependencies", False):
        findings.append({"severity": "blocking", "type": "unapproved_dependency_change"})
    if actual.get("public_contract_changes", 0) and not budget.get("allow_public_contract_changes", False):
        findings.append({"severity": "blocking", "type": "unapproved_public_contract_change"})
    if actual.get("schema_changes", 0) and not budget.get("allow_schema_changes", False):
        findings.append({"severity": "blocking", "type": "unapproved_schema_change"})

    if data.get("route_guard"):
        route_guard_result = run_route_guard(data["route_guard"])
        if route_guard_result.get("status") == "fail":
            findings.append({"severity": "blocking", "type": "route_guard_failed", "message": "Actual diff exceeded the selected route.", "route_guard": route_guard_result})

    for name, status, severity, required, message in iter_checks(checks):
        if status in {"fail", "failed", "blocked", False}:
            findings.append({"severity": severity, "type": "check_failed", "check": name, "message": message})
        elif status in {"not_run", "skipped", None}:
            finding_severity = "blocking" if level == "strict" or required else "warning"
            findings.append({"severity": finding_severity, "type": "check_not_run", "check": name, "message": message})
        elif status in {"warn", "warning"}:
            findings.append({"severity": "warning", "type": "check_warning", "check": name, "message": message})

    commands = data.get("commands", [])
    if require_commands and not commands:
        findings.append({"severity": "blocking", "type": "no_commands_recorded", "message": "Harness v6 standard/strict gates require recorded verification commands unless docs-only."})

    evidence = load_evidence(data)
    findings.extend(validate_evidence(evidence, require_evidence, level))

    blockers = [item for item in findings if item["severity"] == "blocking"]
    warnings = [item for item in findings if item["severity"] != "blocking"]
    return {
        "status": "fail" if blockers else "pass",
        "schema": "project-governor-quality-gate-v2",
        "level": level,
        "quality_level": level,
        "findings": findings,
        "blockers": blockers,
        "warnings": warnings,
        "commands": commands,
        "route_guard": route_guard_result,
        "evidence_required": require_evidence,
        "evidence": evidence,
        "repair_loop_required": bool(blockers),
        "summary": {"blocker_count": len(blockers), "warning_count": len(warnings), "checks_reported": len(iter_checks(checks)), "commands_reported": len(commands)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Project Governor Harness v6 quality gate.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = evaluate(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
