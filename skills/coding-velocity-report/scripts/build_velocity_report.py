#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def clamp(value: float) -> float:
    return max(0, min(100, value))


def report(data: dict[str, Any]) -> dict[str, Any]:
    metrics = data.get("metrics", data)
    repair_rounds = float(metrics.get("repair_rounds", 0))
    drift_findings = float(metrics.get("drift_findings", 0))
    new_files_ratio = float(metrics.get("new_files_ratio", 0))
    gate_pass_rate = float(metrics.get("quality_gate_pass_rate", 1))
    manual_approvals = float(metrics.get("manual_approval_count", 0))
    context_minutes = float(metrics.get("time_to_context_pack_minutes", 0))
    first_patch_minutes = float(metrics.get("time_to_first_patch_minutes", 0))

    quality_score = clamp(100 * gate_pass_rate - repair_rounds * 12 - drift_findings * 10 - new_files_ratio * 30 - manual_approvals * 4)
    velocity_score = clamp(100 - context_minutes * 1.2 - first_patch_minutes * 0.7 - repair_rounds * 8)
    bottlenecks: list[str] = []

    if context_minutes > 20:
        bottlenecks.append("context discovery is slow; improve context-pack-builder hints or registries")
    if repair_rounds > 1:
        bottlenecks.append("repair-loop needed multiple rounds; strengthen test-first planning")
    if drift_findings > 0:
        bottlenecks.append("style or architecture drift found; improve pattern-reuse-engine coverage")
    if new_files_ratio > 0.4:
        bottlenecks.append("high new-file ratio; verify existing patterns were reused")

    return {
        "status": "reported",
        "velocity_score": round(velocity_score, 1),
        "quality_score": round(quality_score, 1),
        "bottlenecks": bottlenecks,
        "recommendations": [
            "keep context packs small and evidence-based",
            "reuse existing patterns before creating files",
            "prefer targeted tests before implementation",
            "run quality-gate before final response",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = report(json.loads(args.input.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
