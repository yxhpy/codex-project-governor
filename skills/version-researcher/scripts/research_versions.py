#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SOURCE_WEIGHTS = {
    "official_changelog": 5,
    "official_release_notes": 5,
    "official_migration_guide": 5,
    "security_advisory": 5,
    "cve": 5,
    "ghsa": 5,
    "eol_policy": 4,
    "deprecation_policy": 4,
    "official_issue": 4,
    "official_pr": 4,
    "rfc": 4,
    "maintainer_blog": 3,
    "third_party_analysis": 2,
    "community_report": 1,
    "unknown": 0,
}

RISK_WEIGHT = {"low": 0, "medium": 2, "high": 5, "critical": 8, "unknown": 3}

NEED_KEYWORDS: dict[str, set[str]] = {
    "version_research": {"release", "version", "changelog", "research", "版本", "研究", "发布", "变更"},
    "upgrade": {"upgrade", "update", "migration", "升级", "更新", "迁移"},
    "memory": {"memory", "memories", "compact", "sleep", "记忆", "睡眠", "整理"},
    "subagents": {"subagent", "parallel", "worker", "并行", "子agent", "子 agent"},
    "automation": {"automation", "cron", "schedule", "定时", "自动化"},
    "security": {"security", "cve", "ghsa", "permission", "sandbox", "安全", "漏洞", "权限"},
    "style": {"style", "component", "design", "ui", "样式", "组件", "设计"},
    "iteration": {"iteration", "rewrite", "greenfield", "迭代", "重写", "新开发"},
    "architecture": {"architecture", "api", "schema", "boundary", "架构", "接口", "边界"},
}

@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int
    suffix: str = ""

    @classmethod
    def parse(cls, value: str) -> "Version":
        text = str(value).strip().lstrip("v")
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)([-+].*)?$", text)
        if not match:
            raise ValueError(f"Invalid semantic version: {value!r}")
        return cls(int(match.group(1)), int(match.group(2)), int(match.group(3)), match.group(4) or "")

    def distance_to(self, other: "Version") -> dict[str, int]:
        return {"major": other.major - self.major, "minor": other.minor - self.minor, "patch": other.patch - self.patch}

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}{self.suffix}"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def infer_needs(text: str) -> set[str]:
    lower = text.lower()
    needs: set[str] = set()
    for need, keywords in NEED_KEYWORDS.items():
        if any(keyword.lower() in lower for keyword in keywords):
            needs.add(need)
    return needs


def version_text(item: dict[str, Any]) -> str:
    parts = [str(item.get(k, "")) for k in ("version", "title", "summary")]
    for key in ("tags", "changes", "breaking_changes", "migration_steps"):
        value = item.get(key, [])
        if isinstance(value, list):
            parts.extend(str(v) for v in value)
    return " ".join(parts)


def evidence_quality(evidence: list[dict[str, Any]]) -> dict[str, Any]:
    if not evidence:
        return {"score": 0, "label": "none", "best_sources": []}
    scored = []
    for item in evidence:
        typ = str(item.get("type", "unknown"))
        scored.append((SOURCE_WEIGHTS.get(typ, 0), typ, item.get("source", "")))
    best = max(score for score, _, _ in scored)
    if best >= 5:
        label = "primary"
    elif best >= 3:
        label = "strong"
    elif best >= 1:
        label = "weak"
    else:
        label = "unknown"
    return {"score": best, "label": label, "best_sources": [source for score, _, source in scored if score == best and source]}


def max_risk(item: dict[str, Any]) -> str:
    risks = item.get("risks", [])
    levels = [str(r.get("level", "unknown")).lower() for r in risks if isinstance(r, dict)]
    if item.get("breaking_changes"):
        levels.append("high")
    if not levels:
        return "low"
    return max(levels, key=lambda level: RISK_WEIGHT.get(level, 3))


def candidate_recommendation(item: dict[str, Any], matched: set[str], quality: dict[str, Any]) -> str:
    risk = max_risk(item)
    breaking = bool(item.get("breaking_changes"))
    has_security = "security" in matched or any("security" in str(e.get("type", "")).lower() for e in item.get("evidence", []))
    if has_security and risk in {"critical", "high"}:
        return "required"
    if breaking or risk == "high":
        return "preview_in_isolation"
    if len(matched) >= 2 and quality["score"] >= 4:
        return "recommended"
    if matched:
        return "consider"
    return "defer"


def analyze(payload: dict[str, Any], request: str) -> dict[str, Any]:
    current = Version.parse(payload["current_version"])
    request_needs = infer_needs(request + " " + payload.get("project_context", "")) or {"upgrade", "version_research"}
    raw_versions = sorted(payload.get("candidate_versions", []), key=lambda item: Version.parse(item["version"]))
    newer = [item for item in raw_versions if Version.parse(item["version"]) > current]
    candidates = []
    for idx, item in enumerate(newer):
        v = Version.parse(item["version"])
        matched = infer_needs(version_text(item)) & request_needs
        quality = evidence_quality(item.get("evidence", []))
        rec = candidate_recommendation(item, matched, quality)
        candidates.append({
            "version": str(v),
            "title": item.get("title", ""),
            "date": item.get("date", ""),
            "summary": item.get("summary", ""),
            "distance": {"from": str(current), "to": str(v), **current.distance_to(v)},
            "skipped_versions_before_this_candidate": [x["version"] for x in newer[:idx]],
            "evidence_quality": quality,
            "matched_needs": sorted(matched),
            "relevant_changes": item.get("changes", []),
            "breaking_changes": item.get("breaking_changes", []),
            "migration_steps": item.get("migration_steps", []),
            "risk": max_risk(item),
            "recommendation": rec,
            "why": build_why(rec, matched, quality, item),
        })
    target = next((c for c in candidates if c["recommendation"] in {"required", "recommended"}), None)
    if target:
        action = "recommend_upgrade" if target["recommendation"] == "recommended" else "upgrade_required_after_confirmation"
    elif candidates:
        target = candidates[0]
        action = "preview_in_isolated_iteration" if target["recommendation"] == "preview_in_isolation" else "consider_after_more_research"
    else:
        action = "pin_current"
    return {
        "subject": payload.get("subject", "unknown"),
        "current_version": str(current),
        "request": request,
        "detected_needs": sorted(request_needs | {"upgrade", "version_research"}),
        "versions_behind": len(newer),
        "candidate_versions": candidates,
        "overall_recommendation": {"action": action, "target_version": target["version"] if target else None},
        "user_choices": [
            {"id": "keep", "label": "Keep current version"},
            {"id": "research", "label": "Research another candidate version"},
            {"id": "preview", "label": "Preview in isolated branch/worktree"},
            {"id": "plan", "label": "Create an upgrade iteration plan"},
            {"id": "apply", "label": "Apply only after explicit confirmation"},
            {"id": "pin", "label": "Pin or reject this version"},
        ],
    }


def build_why(rec: str, matched: set[str], quality: dict[str, Any], item: dict[str, Any]) -> list[str]:
    reasons = []
    if matched:
        reasons.append("Matches needs: " + ", ".join(sorted(matched)))
    else:
        reasons.append("No strong match to the current request")
    reasons.append(f"Evidence quality: {quality['label']}")
    risk = max_risk(item)
    if risk != "low":
        reasons.append(f"Risk level: {risk}")
    if rec == "preview_in_isolation":
        reasons.append("Breaking or high-risk changes require an isolated iteration")
    return reasons


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--request", default="")
    args = parser.parse_args()
    print(json.dumps(analyze(load_json(args.manifest), args.request), indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
