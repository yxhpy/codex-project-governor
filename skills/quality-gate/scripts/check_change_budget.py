#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TRACKED_METRICS = [
    "files_changed",
    "new_files",
    "dependencies_added",
    "public_contract_changes",
    "schema_changes",
]


def check_budget(data: dict[str, Any]) -> dict[str, Any]:
    budget = data.get("budget", {})
    actual = data.get("actual", {})
    findings: list[dict[str, Any]] = []

    for metric in TRACKED_METRICS:
        maximum_key = f"max_{metric}"
        if maximum_key in budget and actual.get(metric, 0) > budget[maximum_key]:
            findings.append(
                {
                    "severity": "blocking",
                    "type": "budget_exceeded",
                    "metric": metric,
                    "actual": actual.get(metric, 0),
                    "max": budget[maximum_key],
                }
            )

    return {"status": "fail" if findings else "pass", "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = check_budget(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
