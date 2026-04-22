#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from _common import load_json, write_json


SAFE_ACTIONS = {"add_if_missing", "replace_from_template"}


def apply(plan_path: Path, do_apply: bool) -> dict[str, Any]:
    plan = load_json(plan_path, {}) or {}
    project = Path(plan["project"])
    plugin_root = Path(plan["plugin_root"])
    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for operation in plan.get("operations", []):
        if operation.get("action") not in SAFE_ACTIONS:
            skipped.append({**operation, "skip_reason": "not_safe_to_apply_automatically"})
            continue

        source = plugin_root / operation["source"]
        destination = project / operation["path"]
        if not source.exists():
            skipped.append({**operation, "skip_reason": "source_missing"})
            continue

        if do_apply:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        applied.append({**operation, "applied": do_apply})

    report = {
        "status": "applied" if do_apply else "dry_run",
        "plan": str(plan_path),
        "applied": applied,
        "skipped": skipped,
        "summary": {"applied_count": len(applied), "skipped_count": len(skipped)},
    }
    if do_apply:
        write_json(plan_path.parent / "APPLY_REPORT.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print(json.dumps(apply(args.plan, args.apply), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
