#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from task_router_config import (
    BUG_TERMS,
    CLEAN_TERMS,
    DOC_TARGET_RE,
    DOCS_ONLY_BLOCKING_SIGNALS,
    DOCS_TERMS,
    GLOBAL_SHARED_TERMS,
    MICRO_TERMS,
    NEGATIVE_PATTERNS,
    PRODUCTION_CHANGE_RE,
    REFACTOR_TERMS,
    RESEARCH_TERMS,
    RISK_SCORE_GROUPS,
    RISK_TERMS,
    TEST_TERMS,
    UI_TERMS,
    UPGRADE_TERMS,
)
from task_router_policy import (
    escalations_for,
    evidence_required_for,
    route_budget,
    route_doc_pack,
    route_guard_requirements,
    subagent_mode,
    workflow,
    workflow_skills,
)


def load(path: Path | None, request: str | None) -> dict[str, Any]:
    if request:
        return {"request": request, "hints": {}}
    if path is None:
        text = sys.stdin.read().strip()
        if not text:
            return {"request": "", "hints": {}}
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return {"request": text, "hints": {}}
        return data if isinstance(data, dict) else {"request": str(data), "hints": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"request": data, "hints": {}} if isinstance(data, str) else data


def has_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def detect_negative_constraints(text: str) -> list[str]:
    return sorted({name for name, pattern in NEGATIVE_PATTERNS if re.search(pattern, text, flags=re.IGNORECASE)})


def strip_negative_constraints(text: str) -> str:
    stripped = text
    for _, pattern in NEGATIVE_PATTERNS:
        stripped = re.sub(pattern, " negative_constraint ", stripped, flags=re.IGNORECASE)
    return stripped


def neutralize_guardrail_terms(text: str, negative_constraints: list[str]) -> str:
    neutralized = text
    replacements = {
        "do_not_change_api": r"\b(api|contract|response|public contract)\b|接口|契约",
        "do_not_change_schema": r"\b(schema|database|db|data model|model)\b|数据表|数据库|模型",
        "do_not_add_dependencies": r"\b(dependenc\w*|package|library|npm|pip)\b|依赖|包",
    }
    for constraint, pattern in replacements.items():
        if constraint in negative_constraints:
            neutralized = re.sub(pattern, " guardrail ", neutralized, flags=re.IGNORECASE)
    return neutralized


def task_text(data: dict[str, Any]) -> str:
    hints = data.get("hints", {}) if isinstance(data.get("hints", {}), dict) else {}
    pieces = [
        str(data.get("request", data.get("user_request", ""))),
        " ".join(map(str, data.get("changed_areas", []))),
        " ".join(map(str, data.get("constraints", []))),
        " ".join(str(value) for value in hints.values()),
    ]
    return " ".join(pieces).lower()


def has_explicit_target(text: str, hints: dict[str, Any]) -> bool:
    if hints.get("target_file") or hints.get("target_files") or hints.get("target_page") or hints.get("target_component"):
        return True
    if re.search(r"[\w./-]+\.(tsx|ts|jsx|js|py|css|scss|md|vue|svelte|html|go|rs|json|yaml|yml|toml)", text, flags=re.IGNORECASE):
        return True
    if DOC_TARGET_RE.search(text):
        return True
    return bool(re.search(r"(只改|only change|only modify|specified page|指定页面|目标文件|这个文件|this file)", text, flags=re.IGNORECASE))


def is_shared_or_global(text: str, hints: dict[str, Any]) -> bool:
    return bool(hints.get("target_is_shared_component") or hints.get("target_is_global_style") or has_any(text, GLOBAL_SHARED_TERMS))


def risk_signals(text: str) -> list[str]:
    negative_constraints = detect_negative_constraints(text)
    active = neutralize_guardrail_terms(strip_negative_constraints(text), negative_constraints)
    signals: list[str] = []
    groups = [
        ("risk_domain", RISK_TERMS),
        ("refactor_signal", REFACTOR_TERMS),
        ("upgrade_signal", UPGRADE_TERMS),
        ("research_signal", RESEARCH_TERMS),
        ("clean_signal", CLEAN_TERMS),
        ("ui_signal", UI_TERMS),
        ("test_signal", TEST_TERMS),
        ("docs_signal", DOCS_TERMS),
        ("bug_signal", BUG_TERMS),
    ]
    for label, terms in groups:
        if has_any(active, terms):
            signals.append(label)
    return signals


def is_docs_only_request(signals: list[str], risk_score: float) -> bool:
    return "docs_signal" in signals and risk_score < 0.35 and not (set(signals) & DOCS_ONLY_BLOCKING_SIGNALS)


def is_test_only_request(signals: list[str], text: str, risk_score: float) -> bool:
    if "test_signal" not in signals or risk_score >= 0.35:
        return False
    if any(signal in signals for signal in ["upgrade_signal", "refactor_signal", "ui_signal", "research_signal", "clean_signal", "risk_domain"]):
        return False
    return not bool(PRODUCTION_CHANGE_RE.search(text))


def compute_risk_score(text: str, hints: dict[str, Any], negative_constraints: list[str]) -> float:
    active = neutralize_guardrail_terms(strip_negative_constraints(text), negative_constraints)
    score = 0.0
    for terms, amount in RISK_SCORE_GROUPS:
        if has_any(active, terms):
            score += amount
    if is_shared_or_global(text, hints):
        score += 0.12
    expected_modified = int(hints.get("expected_modified_files", 0) or 0)
    expected_added = int(hints.get("expected_added_files", 0) or 0)
    if expected_modified >= 8:
        score += 0.12
    if expected_added > 0:
        score += 0.08
    if negative_constraints:
        score += 0.04
    return round(max(0.0, min(0.99, score)), 2)


ConfidenceAdjustment = tuple[bool, float, str]


def confidence_adjustments(text: str, hints: dict[str, Any], risk_score: float, negative_constraints: list[str]) -> list[ConfidenceAdjustment]:
    explicit_target = has_explicit_target(text, hints)
    micro_intent = has_any(text, MICRO_TERMS)
    exact_file_only = bool(hints.get("exact_file_only") or "only this file" in text or "只改这个文件" in text or "只改" in text)
    expected_modified = int(hints.get("expected_modified_files", 1 if explicit_target else 3) or 3)
    return [
        (explicit_target, 0.20, "Explicit target detected."),
        (micro_intent, 0.14, "Local style/copy/spacing intent detected."),
        (exact_file_only or expected_modified <= 1, 0.08, "Small file budget requested or inferred."),
        (bool(negative_constraints), 0.04, "Negative constraints converted to guardrails."),
        (risk_score >= 0.45, -0.22, "Risk score requires conservative route."),
        (is_shared_or_global(text, hints), -0.15, "Shared/global impact detected."),
    ]


def compute_confidence(text: str, hints: dict[str, Any], risk_score: float, negative_constraints: list[str]) -> tuple[float, list[str]]:
    confidence = 0.56
    reasons: list[str] = []
    for applies, amount, reason in confidence_adjustments(text, hints, risk_score, negative_constraints):
        if applies:
            confidence += amount
            reasons.append(reason)
    return max(0.0, min(0.99, round(confidence, 2))), reasons


def routing_context(data: dict[str, Any]) -> dict[str, Any]:
    hints = data.get("hints", {}) if isinstance(data.get("hints", {}), dict) else {}
    text = task_text(data)
    negative_constraints = detect_negative_constraints(text)
    signals = risk_signals(text)
    risk_score = compute_risk_score(text, hints, negative_constraints)
    confidence, reasons = compute_confidence(text, hints, risk_score, negative_constraints)
    explicit_target = has_explicit_target(text, hints)
    micro_intent = has_any(text, MICRO_TERMS)
    shared_or_global = is_shared_or_global(text, hints)
    expected_modified = int(hints.get("expected_modified_files", 1 if explicit_target else 3) or 3)
    expected_added = int(hints.get("expected_added_files", 0) or 0)
    return {
        "hints": hints,
        "text": text,
        "request": str(data.get("request", data.get("user_request", ""))),
        "negative_constraints": negative_constraints,
        "signals": signals,
        "risk_score": risk_score,
        "confidence": confidence,
        "reasons": reasons,
        "task_shape": {
            "explicit_target": explicit_target,
            "micro_intent": micro_intent,
            "shared_or_global": shared_or_global,
            "expected_modified_files": expected_modified,
            "expected_added_files": expected_added,
        },
    }


RouteChoice = tuple[str, str, str, str]


def clean_route(ctx: dict[str, Any]) -> RouteChoice | None:
    return ("clean_reinstall_or_refresh", "standard_lane", "standard", "maintenance") if "clean_signal" in ctx["signals"] else None


def research_route(ctx: dict[str, Any]) -> RouteChoice | None:
    if "research_signal" in ctx["signals"] and "upgrade_signal" not in ctx["signals"]:
        return "research", "research_lane", "standard", "research"
    return None


def upgrade_route(ctx: dict[str, Any]) -> RouteChoice | None:
    if "upgrade_signal" not in ctx["signals"]:
        return None
    risky = ctx["risk_score"] >= 0.45
    return "dependency_upgrade", "risk_lane" if risky else "standard_lane", "strict" if risky else "standard", "upgrade"


def docs_route(ctx: dict[str, Any]) -> RouteChoice | None:
    return ("docs_only", "fast_lane", "light", "docs") if is_docs_only_request(ctx["signals"], ctx["risk_score"]) else None


def test_route(ctx: dict[str, Any]) -> RouteChoice | None:
    if is_test_only_request(ctx["signals"], ctx["text"], ctx["risk_score"]):
        return "test_only", "fast_lane", "light", "test"
    return None


def micro_patch_route(ctx: dict[str, Any]) -> RouteChoice | None:
    shape = ctx["task_shape"]
    if (
        shape["explicit_target"]
        and shape["micro_intent"]
        and ctx["risk_score"] < 0.35
        and not shape["shared_or_global"]
        and shape["expected_modified_files"] <= 1
        and shape["expected_added_files"] == 0
        and ctx["confidence"] >= 0.82
    ):
        return "micro_patch", "fast_lane", "light", "micro_patch"
    return None


def refactor_route(ctx: dict[str, Any]) -> RouteChoice | None:
    return ("refactor", "refactor_lane", "strict", "refactor") if "refactor_signal" in ctx["signals"] else None


def risky_route(ctx: dict[str, Any]) -> RouteChoice | None:
    return ("risky_feature", "risk_lane", "strict", "feature_or_fix") if ctx["risk_score"] >= 0.45 else None


def ui_route(ctx: dict[str, Any]) -> RouteChoice | None:
    shape = ctx["task_shape"]
    if "ui_signal" in ctx["signals"] or shape["shared_or_global"]:
        return "ui_change", "standard_lane", "standard", "ui_change"
    return None


ROUTE_SELECTORS = (
    clean_route,
    research_route,
    upgrade_route,
    docs_route,
    test_route,
    micro_patch_route,
    refactor_route,
    risky_route,
    ui_route,
)


def select_route(ctx: dict[str, Any]) -> RouteChoice:
    for selector in ROUTE_SELECTORS:
        choice = selector(ctx)
        if choice:
            return choice
    return "standard_feature", "standard_lane", "standard", "feature_or_fix"


def classify(data: dict[str, Any]) -> dict[str, Any]:
    ctx = routing_context(data)
    route, lane, quality, intent = select_route(ctx)
    budget = route_budget(route, lane)
    required, skipped = workflow(route)
    guard = route_guard_requirements(route, budget, ctx["negative_constraints"])
    evidence_required = evidence_required_for(route, quality)
    escalations = escalations_for(evidence_required, quality)
    task_shape = dict(ctx["task_shape"])
    task_shape["docs_only"] = route == "docs_only"
    task_shape["test_only"] = route == "test_only"

    return {
        "status": "classified",
        "router_version": "project-governor-harness-v6-router",
        "request": ctx["request"],
        "intent": intent,
        "route": route,
        "lane": lane,
        "quality_level": quality,
        "quality_gate": quality,
        "confidence": ctx["confidence"],
        "risk_score": ctx["risk_score"],
        "risk_signals": ctx["signals"],
        "negative_constraints": ctx["negative_constraints"],
        "task_shape": task_shape,
        "subagent_mode": subagent_mode(route, quality, ctx["confidence"], task_shape["shared_or_global"]),
        "required_skills": workflow_skills(required),
        "required_workflow": required,
        "skipped_workflow": skipped,
        "change_budget": budget,
        "route_doc_pack": route_doc_pack(route, quality),
        "route_guard_requirements": guard,
        "evidence_required": evidence_required,
        "escalate_if": escalations,
        "escalation_triggers": escalations,
        "reasons": ctx["reasons"] or ["Defaulted to Harness v6 safe standard workflow."],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify a task for Project Governor Harness v6.0.")
    parser.add_argument("input", type=Path, nargs="?")
    parser.add_argument("--request")
    args = parser.parse_args()
    print(json.dumps(classify(load(args.input, args.request)), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
