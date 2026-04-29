#!/usr/bin/env python3
"""Check whether a proposed change violates iteration-first governance.

Input JSON fields:
- rewrite_pct_by_file: map of file path to fraction replaced, e.g. 0.45
- dependency_changes: list of dependencies or package-file changes
- new_files: list of new files
- justified_new_files: list of new files justified by the iteration plan
- public_contract_changes: list of public contract changes
- approved_contract_changes: list of approved public contract changes
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REWRITE_THRESHOLD = 0.30
NEW_FILE_THRESHOLD = 3


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rewrite_findings(data: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for file_path, pct in data.get("rewrite_pct_by_file", {}).items():
        try:
            numeric_pct = float(pct)
        except (TypeError, ValueError):
            findings.append({"severity": "blocking", "type": "invalid_rewrite_metric", "file": file_path, "value": pct})
            continue
        if numeric_pct > REWRITE_THRESHOLD:
            findings.append({
                "severity": "blocking",
                "type": "rewrite_risk",
                "file": file_path,
                "pct": numeric_pct,
                "threshold": REWRITE_THRESHOLD,
                "message": "Large replacement detected; require explicit rewrite approval or a smaller patch."
            })
    return findings


def dependency_findings(data: dict[str, Any]) -> list[dict[str, Any]]:
    dependency_changes = data.get("dependency_changes", [])
    if dependency_changes:
        return [{
            "severity": "blocking",
            "type": "dependency_change_requires_decision",
            "items": dependency_changes,
            "message": "Production dependency changes require a decision note and alternatives analysis."
        }]
    return []


def new_file_findings(data: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    new_files = set(data.get("new_files", []))
    justified = set(data.get("justified_new_files", []))
    unjustified = sorted(new_files - justified)
    if unjustified:
        findings.append({
            "severity": "blocking",
            "type": "new_files_without_justification",
            "items": unjustified,
            "message": "Every new file must be justified in the iteration plan."
        })
    if len(new_files) > NEW_FILE_THRESHOLD:
        findings.append({
            "severity": "warning",
            "type": "many_new_files",
            "count": len(new_files),
            "threshold": NEW_FILE_THRESHOLD,
            "message": "Large feature footprint; verify this is not greenfield redevelopment."
        })
    return findings


def contract_findings(data: dict[str, Any]) -> list[dict[str, Any]]:
    contract_changes = set(data.get("public_contract_changes", []))
    approved = set(data.get("approved_contract_changes", []))
    unapproved_contracts = sorted(contract_changes - approved)
    if unapproved_contracts:
        return [{
            "severity": "blocking",
            "type": "public_contract_change_requires_decision",
            "items": unapproved_contracts,
            "message": "Public contract changes require explicit approval and docs updates."
        }]
    return []


def check(data: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    findings.extend(rewrite_findings(data))
    findings.extend(dependency_findings(data))
    findings.extend(new_file_findings(data))
    findings.extend(contract_findings(data))

    blocking = any(f["severity"] == "blocking" for f in findings)
    return {"status": "fail" if blocking else "pass", "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check iteration compliance from a JSON input file.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = check(load_json(args.input))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
