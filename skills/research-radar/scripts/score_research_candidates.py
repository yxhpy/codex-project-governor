#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SOURCE_WEIGHT = {
    "official_docs": 5,
    "official_changelog": 5,
    "official_release_notes": 5,
    "research_paper": 5,
    "standard": 4,
    "official_repo": 4,
    "vendor_blog": 3,
    "third_party_analysis": 2,
    "community_post": 1,
    "unknown": 0,
}
RISK_WEIGHT = {"low": 3, "medium": 0, "high": -4, "critical": -8, "unknown": -1}
MATURITY_WEIGHT = {"stable": 4, "available": 3, "beta": 0, "preview": -1, "experimental": -3, "deprecated": -8, "unknown": -1}
COST_WEIGHT = {"low": 2, "medium": 0, "high": -3, "unknown": -1}

NEED_KEYWORDS: dict[str, set[str]] = {
    "memory": {"memory", "memories", "compact", "compaction", "sleep", "dream", "reflection", "记忆", "整理", "睡眠"},
    "automation": {"automation", "automations", "schedule", "cron", "worktree", "定时", "自动化"},
    "subagents": {"subagent", "subagents", "parallel", "swarm", "并行", "子agent", "子 agent"},
    "research": {"research", "radar", "evidence", "source", "compare", "研究", "证据", "来源"},
    "iteration": {"iteration", "iterative", "rewrite", "greenfield", "迭代", "重写"},
    "style": {"style", "component", "ui", "design", "样式", "组件"},
    "security": {"security", "sandbox", "permission", "rules", "hooks", "secret", "安全", "权限", "密钥"},
    "upgrade": {"upgrade", "version", "release", "升级", "版本"},
    "governance": {"governance", "policy", "rules", "score", "治理", "规范", "规则"},
}


def normalize(values: list[str]) -> set[str]:
    return {str(v).strip().lower() for v in values if str(v).strip()}


def infer_needs(text: str) -> set[str]:
    lower = text.lower()
    found = set()
    for need, keywords in NEED_KEYWORDS.items():
        if any(k.lower() in lower for k in keywords):
            found.add(need)
    return found


def candidate_text(item: dict[str, Any]) -> str:
    parts = [str(item.get(k, "")) for k in ("id", "title", "summary", "source_type", "source", "risk", "maturity", "implementation_cost")]
    for key in ("tags", "evidence", "concerns", "recommended_for"):
        value = item.get(key, [])
        if isinstance(value, list):
            parts.extend(str(v) for v in value)
    return " ".join(parts)


def matched_needs(item: dict[str, Any], needs: set[str]) -> list[str]:
    tags = normalize(item.get("tags", [])) if isinstance(item.get("tags", []), list) else set()
    inferred = infer_needs(candidate_text(item))
    return sorted(needs & (tags | inferred))


def score(item: dict[str, Any], matches: list[str]) -> int:
    source_type = str(item.get("source_type", "unknown")).lower()
    risk = str(item.get("risk", "unknown")).lower()
    maturity = str(item.get("maturity", "unknown")).lower()
    cost = str(item.get("implementation_cost", "unknown")).lower()
    evidence_count = len(item.get("evidence", [])) if isinstance(item.get("evidence", []), list) else 0
    return (
        len(matches) * 4
        + SOURCE_WEIGHT.get(source_type, 0)
        + RISK_WEIGHT.get(risk, -1)
        + MATURITY_WEIGHT.get(maturity, -1)
        + COST_WEIGHT.get(cost, -1)
        + min(evidence_count, 3)
    )


def recommendation(score_value: int, item: dict[str, Any]) -> str:
    maturity = str(item.get("maturity", "unknown")).lower()
    risk = str(item.get("risk", "unknown")).lower()
    breaking = bool(item.get("breaking", False))
    if maturity == "deprecated":
        return "reject"
    if breaking or risk in {"high", "critical"}:
        return "spike" if score_value >= 7 else "watch"
    if maturity in {"experimental", "preview", "beta"}:
        return "spike" if score_value >= 6 else "watch"
    if score_value >= 16:
        return "adopt_now"
    if score_value >= 8:
        return "spike"
    if score_value >= 3:
        return "watch"
    return "reject"


def analyze(payload: dict[str, Any], needs: set[str]) -> dict[str, Any]:
    if not needs:
        needs = set(payload.get("project_needs", [])) or {"governance"}
    items = []
    for raw in payload.get("candidates", []):
        item = dict(raw)
        matches = matched_needs(item, needs)
        score_value = score(item, matches)
        item["matched_needs"] = matches
        item["score"] = score_value
        item["recommendation"] = recommendation(score_value, item)
        item["reasons"] = build_reasons(item)
        items.append(item)
    items.sort(key=lambda x: (-x["score"], x.get("id", "")))
    summary = {name: [item["id"] for item in items if item["recommendation"] == name] for name in ["adopt_now", "spike", "watch", "reject"]}
    return {
        "project": payload.get("project", "unknown"),
        "generated_at": payload.get("generated_at", "unknown"),
        "needs": sorted(needs),
        "candidates": items,
        "summary": summary,
        "user_choices": [
            {"id": "0", "label": "Do not act"},
            {"id": "1", "label": "Create research report only"},
            {"id": "2", "label": "Create isolated spike branch/worktree"},
            {"id": "3", "label": "Implement recommended low-risk scope"},
            {"id": "4", "label": "Choose a specific candidate"},
        ],
    }


def build_reasons(item: dict[str, Any]) -> list[str]:
    reasons = []
    if item["matched_needs"]:
        reasons.append("Matches needs: " + ", ".join(item["matched_needs"]))
    else:
        reasons.append("No strong match to declared needs")
    reasons.append(f"Evidence source type: {item.get('source_type', 'unknown')}")
    reasons.append(f"Risk: {item.get('risk', 'unknown')}; maturity: {item.get('maturity', 'unknown')}")
    if item.get("breaking"):
        reasons.append("Breaking or workflow-changing candidate; isolate as spike")
    return reasons


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--need", action="append", default=[])
    args = parser.parse_args()
    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    needs = set(args.need) | set(payload.get("project_needs", []))
    print(json.dumps(analyze(payload, needs), indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
