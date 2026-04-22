#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


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

    status = "ready" if not blockers else "not_ready"
    return {
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "commands_verified": data.get("commands_verified", []),
        "required_before_merge": [] if status == "ready" else blockers,
    }


eval = evaluate_readiness


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = evaluate_readiness(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
