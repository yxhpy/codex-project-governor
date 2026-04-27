#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_manifest(task_id: str, route: str) -> dict[str, Any]:
    return {
        "schema": "project-governor-evidence-v1",
        "task_id": task_id,
        "route": route,
        "created_at": utc_now(),
        "acceptance_criteria": [],
        "tests": [],
        "reviews": {
            "spec_compliance": "not_run",
            "code_quality": "not_run",
        },
        "docs_refresh": {
            "needed": False,
            "reason": "not evaluated",
            "files_updated": [],
        },
    }


def merge_manifest(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            nested = dict(merged[key])
            nested.update(value)
            merged[key] = nested
        else:
            merged[key] = value
    return merged


def validate(manifest: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if not manifest.get("task_id"):
        blockers.append("task_id is missing")
    if not manifest.get("route"):
        blockers.append("route is missing")
    for index, item in enumerate(manifest.get("acceptance_criteria", [])):
        if not isinstance(item, dict) or not item.get("criterion") or not item.get("proof"):
            blockers.append(f"acceptance_criteria[{index}] must include criterion and proof")
    for index, item in enumerate(manifest.get("tests", [])):
        if not isinstance(item, dict) or not item.get("command") or item.get("status") not in {"passed", "pass", True, "failed", "fail", "not_run", "skipped"}:
            blockers.append(f"tests[{index}] must include command and valid status")
    docs_refresh = manifest.get("docs_refresh", {})
    if isinstance(docs_refresh, dict) and docs_refresh.get("needed") is True and not docs_refresh.get("files_updated"):
        blockers.append("docs_refresh.needed=true requires files_updated")
    return {"status": "pass" if not blockers else "fail", "blockers": blockers}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or validate a Project Governor Harness v6 evidence manifest.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--task-id", default="task")
    parser.add_argument("--route", default="standard_feature")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()

    if args.input:
        incoming = json.loads(args.input.read_text(encoding="utf-8"))
    else:
        incoming = {}
    manifest = merge_manifest(default_manifest(args.task_id, args.route), incoming)
    result = validate(manifest)
    if args.validate:
        print(json.dumps({"status": result["status"], "validation": result, "manifest": manifest}, indent=2, ensure_ascii=False))
        return 0 if result["status"] == "pass" else 1
    output = args.output or args.project / ".project-governor" / "evidence" / args.task_id / "EVIDENCE.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "written", "path": str(output), "validation": result}, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
