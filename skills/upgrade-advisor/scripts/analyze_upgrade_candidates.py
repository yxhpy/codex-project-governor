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


def recommendation_for(dep: dict[str, Any], project_requirements: list[str], distance: dict[str, Any]) -> tuple[str, int, list[str]]:
    reasons: list[str] = []
    score = 0

    security = bool(dep.get("security", False))
    eol = bool(dep.get("eol", False))
    breaking = bool(dep.get("breaking", False))
    required_by = normalize_list(dep.get("required_by"))
    wanted_by = normalize_list(dep.get("wanted_by"))
    requirement_matches = normalize_list(dep.get("requirement_matches"))
    risk = str(dep.get("risk", "unknown")).lower()

    if security:
        score += 60
        reasons.append("security issue present")
    if eol:
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

    if distance.get("known") and distance.get("major", 0) >= 1:
        score += 8
        reasons.append(f"behind by {distance['major']} major version(s)")
    elif distance.get("known") and distance.get("minor", 0) >= 2:
        score += 5
        reasons.append(f"behind by {distance['minor']} minor version(s)")

    score += RISK_WEIGHT.get(risk, RISK_WEIGHT["unknown"])
    if risk in {"medium", "high", "unknown"}:
        reasons.append(f"migration risk is {risk}")
    if breaking:
        score -= 12
        reasons.append("candidate includes breaking changes")

    if security or eol or required_by:
        return "upgrade_required", score, reasons
    if score >= 35:
        return "recommend_upgrade", score, reasons
    if score >= 15:
        return "consider_upgrade", score, reasons
    if breaking or risk == "high":
        return "defer", score, reasons or ["upgrade risk outweighs current requirement relevance"]
    return "defer", score, reasons or ["no direct relevance to the current request was provided"]


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    project_requirements = normalize_list(data.get("project_requirements"))
    dependencies = data.get("dependencies", [])
    results: list[dict[str, Any]] = []

    for dep in dependencies:
        current = Version.parse(dep.get("current"))
        latest = Version.parse(dep.get("latest"))
        distance = version_distance(current, latest)
        skipped = count_skipped_versions(normalize_list(dep.get("available_versions")), current, latest)
        recommendation, score, reasons = recommendation_for(dep, project_requirements, distance)
        risk = str(dep.get("risk", "unknown")).lower()
        result = {
            "name": dep.get("name"),
            "type": dep.get("type", "unknown"),
            "current": dep.get("current"),
            "candidate": dep.get("latest"),
            "recommended_target": dep.get("safe_target") or dep.get("latest"),
            "version_distance": distance,
            "skipped_versions": skipped,
            "requirement_relevance": {
                "required_by": normalize_list(dep.get("required_by")),
                "wanted_by": normalize_list(dep.get("wanted_by")),
                "matches": normalize_list(dep.get("requirement_matches")),
            },
            "risk": risk,
            "breaking": bool(dep.get("breaking", False)),
            "recommendation": recommendation,
            "score": score,
            "why": reasons,
            "notes": dep.get("notes", ""),
            "choices": ["upgrade_now", "plan_upgrade_iteration", "defer", "reject_or_pin"],
        }
        results.append(result)

    priority = {"upgrade_required": 0, "recommend_upgrade": 1, "consider_upgrade": 2, "defer": 3, "reject_or_pin": 4}
    results.sort(key=lambda item: (priority.get(str(item["recommendation"]), 9), -int(item["score"])))

    summary = {
        "upgrade_required": sum(1 for item in results if item["recommendation"] == "upgrade_required"),
        "recommend_upgrade": sum(1 for item in results if item["recommendation"] == "recommend_upgrade"),
        "consider_upgrade": sum(1 for item in results if item["recommendation"] == "consider_upgrade"),
        "defer": sum(1 for item in results if item["recommendation"] == "defer"),
        "reject_or_pin": sum(1 for item in results if item["recommendation"] == "reject_or_pin"),
    }
    return {
        "status": "review_required" if results else "no_candidates",
        "project_requirements": project_requirements,
        "summary": summary,
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
