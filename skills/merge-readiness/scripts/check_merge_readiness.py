#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_evidence(data: dict[str, Any]) -> dict[str, Any] | None:
    evidence = data.get("evidence")
    if isinstance(evidence, dict):
        return evidence
    path = data.get("evidence_manifest") or data.get("evidence_path")
    if path and Path(path).exists():
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return None


def evidence_ready(evidence: dict[str, Any] | None) -> tuple[bool, list[str]]:
    if evidence is None:
        return False, ["evidence manifest is missing"]
    issues: list[str] = []
    criteria = evidence.get("acceptance_criteria", [])
    if not criteria:
        issues.append("evidence has no acceptance criteria mapping")
    for index, criterion in enumerate(criteria):
        if not isinstance(criterion, dict) or not criterion.get("criterion") or not criterion.get("proof"):
            issues.append(f"acceptance criterion {index} is incomplete")
    for index, test in enumerate(evidence.get("tests", [])):
        if not isinstance(test, dict) or not test.get("command") or test.get("status") not in {"passed", "pass", True}:
            issues.append(f"test evidence {index} is not passing")
    docs_refresh = evidence.get("docs_refresh", {})
    if isinstance(docs_refresh, dict) and docs_refresh.get("needed") is True and not docs_refresh.get("files_updated"):
        issues.append("docs refresh is needed but no files were updated")
    return not issues, issues


def evaluate_readiness(data: dict[str, Any]) -> dict[str, Any]:
    blockers = list(data.get("blockers", []))
    warnings = list(data.get("warnings", []))
    quality_gate = data.get("quality_gate", {})
    if quality_gate.get("status") not in {"pass", "passed", True}:
        blockers.append("quality gate has not passed")
    if data.get("required_docs_missing"):
        blockers.append("required docs or memory updates are missing")
    if data.get("approval_required") and not data.get("approval_recorded"):
        blockers.append("required manual approval is missing")
    if data.get("open_repair_items"):
        blockers.append("repair-loop still has unresolved items")

    require_evidence = bool(data.get("require_evidence") or quality_gate.get("evidence_required") or quality_gate.get("level") == "strict" or quality_gate.get("quality_level") == "strict")
    evidence = load_evidence(data)
    if require_evidence:
        ok, issues = evidence_ready(evidence)
        if not ok:
            blockers.extend(issues)
    elif evidence is None:
        warnings.append("no evidence manifest supplied; Harness v6 recommends evidence for all non-trivial merges")

    status = "ready" if not blockers else "not_ready"
    return {
        "status": status,
        "schema": "project-governor-merge-readiness-v2",
        "blockers": blockers,
        "warnings": warnings,
        "commands_verified": data.get("commands_verified", []),
        "evidence_required": require_evidence,
        "evidence_present": evidence is not None,
        "required_before_merge": [] if status == "ready" else blockers,
    }


eval = evaluate_readiness


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Project Governor Harness v6 merge readiness.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = evaluate_readiness(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
