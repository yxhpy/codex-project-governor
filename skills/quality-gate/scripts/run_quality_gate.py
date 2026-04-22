#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LEVELS = {"light", "standard", "strict"}


def normalize_level(value: object) -> str:
    return value if isinstance(value, str) and value in LEVELS else "standard"


def check_status(value: object) -> object:
    if isinstance(value, dict):
        return value.get("status")
    return value


def evaluate(data: dict[str, Any]) -> dict[str, Any]:
    level = normalize_level(data.get("level", "standard"))
    findings: list[dict[str, Any]] = []
    budget = data.get("change_budget", {})
    actual = data.get("actual", {})
    checks = data.get("checks", {})

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

    for name, result in checks.items():
        status = check_status(result)
        if status in {"fail", "failed", False}:
            findings.append({"severity": "blocking", "type": "check_failed", "check": name})
        elif status in {"not_run", "skipped", None}:
            severity = "blocking" if level == "strict" else "warning"
            findings.append({"severity": severity, "type": "check_not_run", "check": name})

    if level in {"standard", "strict"} and not data.get("commands", []):
        findings.append({"severity": "warning", "type": "no_commands_recorded"})

    has_blocker = any(item["severity"] == "blocking" for item in findings)
    return {
        "status": "fail" if has_blocker else "pass",
        "level": level,
        "findings": findings,
        "commands": data.get("commands", []),
        "repair_loop_required": has_blocker,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = evaluate(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
