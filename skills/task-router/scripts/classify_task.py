#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


RISK = {
    "auth",
    "authorization",
    "permission",
    "role",
    "payment",
    "billing",
    "security",
    "secret",
    "token",
    "privacy",
    "pii",
    "schema",
    "database",
    "webhook",
    "external",
    "integration",
}
REFACTOR = {"refactor", "restructure", "cleanup", "reorganize", "extract", "split", "rewrite"}
UPGRADE = {"upgrade", "update dependency", "bump", "version", "migrate to", "sdk", "framework"}
UI = {"ui", "style", "component", "screen", "page", "layout", "button", "modal", "theme", "design", "dashboard", "widget"}
TEST = {"test", "spec", "coverage", "fixture", "mock"}
DOCS = {"docs", "documentation", "readme", "guide", "manual"}
BUG = {"bug", "fix", "broken", "error", "crash", "regression"}
SIGNAL_GROUPS = [
    ("risk_domain", RISK),
    ("refactor_signal", REFACTOR),
    ("upgrade_signal", UPGRADE),
    ("ui_signal", UI),
    ("test_signal", TEST),
    ("docs_signal", DOCS),
    ("bug_signal", BUG),
]


def load(path: Path | None, request: str | None) -> dict[str, Any]:
    if path is None:
        return {"request": request or ""}
    return json.loads(path.read_text(encoding="utf-8"))


def has_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def task_text(data: dict[str, Any]) -> str:
    return " ".join(
        [
            str(data.get("request", "")),
            " ".join(map(str, data.get("changed_areas", []))),
            " ".join(map(str, data.get("constraints", []))),
        ]
    ).lower()


def route_for(signals: list[str], text: str) -> tuple[str, str, str]:
    signal_set = set(signals)
    if "docs_signal" in signal_set and not signal_set - {"docs_signal"}:
        return "docs_only", "fast", "light"
    if "test_signal" in signal_set and not any(signal in signal_set for signal in ["risk_domain", "upgrade_signal", "refactor_signal", "ui_signal"]):
        return "test_only", "fast", "light"
    if "upgrade_signal" in signal_set:
        return "dependency_upgrade", "risk", "strict"
    if "refactor_signal" in signal_set:
        return "refactor", "refactor", "strict"
    if "risk_domain" in signal_set:
        return "risky_feature", "risk", "strict"
    if "ui_signal" in signal_set:
        return "ui_change", "standard", "standard"
    if "bug_signal" in signal_set and len(text.split()) <= 18:
        return "tiny_patch", "fast", "light"
    return "standard_feature", "standard", "standard"


def change_budget(data: dict[str, Any], route: str, lane: str) -> dict[str, Any]:
    return {
        "max_files_changed": 3 if lane == "fast" else 8 if lane == "standard" else 12,
        "max_new_files": 1 if lane == "fast" else 3 if lane == "standard" else 4,
        "allow_dependencies": bool(data.get("allow_dependencies", False)) and route == "dependency_upgrade",
        "allow_public_contract_changes": lane == "risk",
        "allow_schema_changes": route in {"migration", "risky_feature"},
        "allow_refactor": route == "refactor",
    }


def required_skills(route: str) -> list[str]:
    if route == "dependency_upgrade":
        return ["version-researcher", "upgrade-advisor", "iteration-planner", "quality-gate", "merge-readiness"]

    skills = ["context-pack-builder"]
    if route not in {"docs_only", "test_only"}:
        skills.append("pattern-reuse-engine")
    if route != "docs_only":
        skills.append("test-first-synthesizer")
    skills.extend(["parallel-feature-builder" if route != "docs_only" else "quality-gate", "quality-gate", "merge-readiness"])
    if route == "risky_feature":
        skills.insert(0, "iteration-planner")
    return skills


def classify(data: dict[str, Any]) -> dict[str, Any]:
    text = task_text(data)
    signals = [label for label, terms in SIGNAL_GROUPS if has_any(text, terms)]
    route, lane, quality = route_for(signals, text)
    return {
        "status": "classified",
        "route": route,
        "lane": lane,
        "quality_level": quality,
        "risk_signals": signals,
        "required_skills": required_skills(route),
        "change_budget": change_budget(data, route, lane),
        "escalate_if": [
            "change budget exceeded",
            "new dependency required",
            "public API or schema change discovered",
            "quality gate fails after repair-loop limit",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, nargs="?")
    parser.add_argument("--request")
    args = parser.parse_args()
    print(json.dumps(classify(load(args.input, args.request)), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
