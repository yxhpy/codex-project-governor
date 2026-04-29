#!/usr/bin/env python3
"""Analyze upgrade candidates from an offline JSON inventory.

Input JSON shape:
{
  "project_requirements": ["need new dashboard feature"],
  "dependencies": [
    {
      "name": "react",
      "type": "runtime",
      "current": "18.2.0",
      "latest": "19.1.0",
      "available_versions": ["18.2.0", "18.3.1", "19.0.0", "19.1.0"],
      "wanted_by": ["new dashboard feature"],
      "required_by": [],
      "security": false,
      "eol": false,
      "breaking": true,
      "risk": "medium",
      "notes": "Requires compatibility checks."
    }
  ]
}

The script is intentionally offline. It does not query package registries.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

VERSION_RE = re.compile(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?")
RISK_WEIGHT = {"low": 0, "medium": -8, "high": -25, "unknown": -12}


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: Any) -> "Version | None":
        if value is None:
            return None
        text = str(value).strip()
        # Remove common package-manager range prefixes.
        text = re.sub(r"^[\^~<>=!\s]+", "", text)
        match = VERSION_RE.search(text)
        if not match:
            return None
        major = int(match.group(1))
        minor = int(match.group(2) or 0)
        patch = int(match.group(3) or 0)
        return cls(major, minor, patch)

    def as_dict(self) -> dict[str, int]:
        return {"major": self.major, "minor": self.minor, "patch": self.patch}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def version_distance(current: Version | None, latest: Version | None) -> dict[str, Any]:
    if current is None or latest is None:
        return {"known": False, "major": None, "minor": None, "patch": None}
    return {
        "known": True,
        "major": max(latest.major - current.major, 0),
        "minor": max(latest.minor - current.minor, 0) if latest.major == current.major else latest.minor,
        "patch": max(latest.patch - current.patch, 0) if latest.major == current.major and latest.minor == current.minor else latest.patch,
    }


def count_skipped_versions(available_versions: list[Any], current: Version | None, latest: Version | None) -> int | None:
    if current is None or latest is None or not available_versions:
        return None
    parsed = sorted({v for raw in available_versions if (v := Version.parse(raw)) is not None})
    return sum(1 for version in parsed if current < version <= latest)


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def urgency_score(dep: dict[str, Any], required_by: list[str], wanted_by: list[str], requirement_matches: list[str]) -> tuple[int, list[str]]:
    reasons: list[str] = []
    score = 0
    if dep.get("security", False):
        score += 60
        reasons.append("security issue present")
    if dep.get("eol", False):
        score += 50
        reasons.append("current version is EOL or unsupported")
    if required_by:
        score += 45
        reasons.append("required by: " + "; ".join(required_by))
    if wanted_by:
        score += 30
        reasons.append("may unlock requested capability: " + "; ".join(wanted_by))
    if requirement_matches:
        score += 20
        reasons.append("matches project requirement: " + "; ".join(requirement_matches))
    return score, reasons


def distance_score(distance: dict[str, Any]) -> tuple[int, list[str]]:
    if distance.get("known") and distance.get("major", 0) >= 1:
        return 8, [f"behind by {distance['major']} major version(s)"]
    if distance.get("known") and distance.get("minor", 0) >= 2:
        return 5, [f"behind by {distance['minor']} minor version(s)"]
    return 0, []


def migration_score(risk: str, breaking: bool) -> tuple[int, list[str]]:
    reasons: list[str] = []
    score = 0
    score += RISK_WEIGHT.get(risk, RISK_WEIGHT["unknown"])
    if risk in {"medium", "high", "unknown"}:
        reasons.append(f"migration risk is {risk}")
    if breaking:
        score -= 12
        reasons.append("candidate includes breaking changes")
    return score, reasons


def recommendation_name(score: int, required: bool, breaking: bool, risk: str) -> str:
    if required:
        return "upgrade_required"
    if score >= 35:
        return "recommend_upgrade"
    if score >= 15:
        return "consider_upgrade"
    if breaking or risk == "high":
        return "defer"
    return "defer"


def recommendation_for(dep: dict[str, Any], project_requirements: list[str], distance: dict[str, Any]) -> tuple[str, int, list[str]]:
    required_by = normalize_list(dep.get("required_by"))
    wanted_by = normalize_list(dep.get("wanted_by"))
    requirement_matches = normalize_list(dep.get("requirement_matches"))
    risk = str(dep.get("risk", "unknown")).lower()
    breaking = bool(dep.get("breaking", False))
    required = bool(dep.get("security", False) or dep.get("eol", False) or required_by)

    urgency, urgency_reasons = urgency_score(dep, required_by, wanted_by, requirement_matches)
    distance_points, distance_reasons = distance_score(distance)
    migration_points, migration_reasons = migration_score(risk, breaking)
    score = urgency + distance_points + migration_points
    reasons = urgency_reasons + distance_reasons + migration_reasons

    recommendation = recommendation_name(score, required, breaking, risk)
    if recommendation == "defer" and not reasons:
        reasons = ["upgrade risk outweighs current requirement relevance"] if breaking or risk == "high" else ["no direct relevance to the current request was provided"]
    return recommendation, score, reasons


def candidate_result(dep: dict[str, Any], project_requirements: list[str]) -> dict[str, Any]:
    current = Version.parse(dep.get("current"))
    latest = Version.parse(dep.get("latest"))
    distance = version_distance(current, latest)
    recommendation, score, reasons = recommendation_for(dep, project_requirements, distance)
    return {
        "name": dep.get("name"),
        "type": dep.get("type", "unknown"),
        "current": dep.get("current"),
        "candidate": dep.get("latest"),
        "recommended_target": dep.get("safe_target") or dep.get("latest"),
        "version_distance": distance,
        "skipped_versions": count_skipped_versions(normalize_list(dep.get("available_versions")), current, latest),
        "requirement_relevance": {
            "required_by": normalize_list(dep.get("required_by")),
            "wanted_by": normalize_list(dep.get("wanted_by")),
            "matches": normalize_list(dep.get("requirement_matches")),
        },
        "risk": str(dep.get("risk", "unknown")).lower(),
        "breaking": bool(dep.get("breaking", False)),
        "recommendation": recommendation,
        "score": score,
        "why": reasons,
        "notes": dep.get("notes", ""),
        "choices": ["upgrade_now", "plan_upgrade_iteration", "defer", "reject_or_pin"],
    }


def sorted_results(dependencies: list[dict[str, Any]], project_requirements: list[str]) -> list[dict[str, Any]]:
    results = [candidate_result(dep, project_requirements) for dep in dependencies]
    priority = {"upgrade_required": 0, "recommend_upgrade": 1, "consider_upgrade": 2, "defer": 3, "reject_or_pin": 4}
    results.sort(key=lambda item: (priority.get(str(item["recommendation"]), 9), -int(item["score"])))
    return results


def summary_for(results: list[dict[str, Any]]) -> dict[str, int]:
    labels = ["upgrade_required", "recommend_upgrade", "consider_upgrade", "defer", "reject_or_pin"]
    return {label: sum(1 for item in results if item["recommendation"] == label) for label in labels}


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    project_requirements = normalize_list(data.get("project_requirements"))
    results = sorted_results(data.get("dependencies", []), project_requirements)
    return {
        "status": "review_required" if results else "no_candidates",
        "project_requirements": project_requirements,
        "summary": summary_for(results),
        "candidates": results,
        "policy": "Advisory only. Do not edit manifests or install packages until the user selects an upgrade path.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze offline upgrade candidates and recommend user-selectable actions.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(load_json(args.input)), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
