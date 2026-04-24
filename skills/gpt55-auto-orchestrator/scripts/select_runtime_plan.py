#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

RISK_WORDS = {
    "auth", "authorization", "permission", "rbac", "payment", "billing", "security", "privacy",
    "schema", "migration", "database", "webhook", "oauth", "token", "pii", "encryption",
    "api contract", "external integration", "data loss", "production", "compliance",
}
MICRO_WORDS = {"style", "spacing", "margin", "padding", "color", "copy", "typo", "text", "label", "css", "class"}
RESEARCH_WORDS = {"research", "compare", "investigate", "调研", "研究", "对比"}
UPGRADE_WORDS = {"upgrade", "migrate", "version", "release", "dependency", "升级", "迁移", "版本"}
CLEAN_WORDS = {"clean", "reinstall", "refresh", "hygiene", "trash", "quarantine", "重装", "清理", "刷新"}
DESIGN_WORDS = {"design", "design.md", "visual", "token", "typography", "设计", "样式"}

DEFAULT_MODELS = {
    "primary": "gpt-5.5",
    "fallback_primary": "gpt-5.4",
    "fast_scout": "gpt-5.4-mini",
    "high_reasoning": "gpt-5.5",
}


def load_payload(path: str | None) -> dict[str, Any]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    raw = sys.stdin.read().strip()
    if not raw:
        raise SystemExit("Provide an input JSON file or JSON on stdin.")
    return json.loads(raw)


def low(text: str) -> str:
    return (text or "").lower()


def has_any(text: str, words: set[str]) -> bool:
    t = low(text)
    return any(w in t for w in words)


def explicit_target_file(text: str) -> bool:
    return bool(re.search(r"(?:src|app|pages|components|docs|tests?)/[^\s]+\.[a-zA-Z0-9]+", text))


def normalized_risk_text(request: str) -> str:
    text = low(request)
    for pattern in [
        r"do not change (?:the )?(?:api|schema|api schema|database|db)",
        r"don['’]?t change (?:the )?(?:api|schema|api schema|database|db)",
        r"no (?:api|schema|api schema|database|db) changes?",
        r"不要改(?:api|schema|数据库|接口)",
        r"不改(?:api|schema|数据库|接口)",
    ]:
        text = re.sub(pattern, " negative_constraint ", text)
    return text


def detect_route(request: str, payload: dict[str, Any]) -> tuple[str, str, str, list[str]]:
    provided = payload.get("route")
    quality = payload.get("quality_level") or payload.get("quality_gate")
    reasons: list[str] = []
    if provided:
        route = str(provided)
        reasons.append("Route provided by upstream task-router.")
    elif has_any(request, CLEAN_WORDS):
        route = "clean_reinstall_or_refresh"
        reasons.append("Request asks for reinstall, refresh, hygiene, or latest-mode application.")
    elif has_any(request, RESEARCH_WORDS):
        route = "research"
        reasons.append("Request asks for research/comparison before implementation.")
    elif has_any(request, UPGRADE_WORDS):
        route = "upgrade_or_migration"
        reasons.append("Request asks for upgrade/migration/version work.")
    elif has_any(request, DESIGN_WORDS) and "design.md" in low(request):
        route = "design_governance"
        reasons.append("Request explicitly mentions DESIGN.md or design governance.")
    elif explicit_target_file(request) and has_any(request, MICRO_WORDS):
        route = "micro_patch"
        reasons.append("Explicit target file plus local style/copy/edit terms detected.")
    elif has_any(normalized_risk_text(request), RISK_WORDS):
        route = "risky_feature"
        reasons.append("Risk-sensitive terms detected.")
    else:
        route = "standard_feature"
        reasons.append("Defaulted to standard feature workflow.")

    if route == "micro_patch":
        lane, gate = "fast_lane", "light"
    elif route in {"risky_feature", "upgrade_or_migration"}:
        lane, gate = "risk_lane", "strict"
    elif route in {"research", "clean_reinstall_or_refresh", "design_governance"}:
        lane, gate = "standard_lane", "standard"
    else:
        lane, gate = "standard_lane", "standard"
    if quality:
        gate = str(quality)
    return route, lane, gate, reasons


def choose_models(route: str, gate: str, prefer_speed: bool, available: set[str]) -> dict[str, Any]:
    primary = "gpt-5.5" if "gpt-5.5" in available else "gpt-5.4"
    scout = "gpt-5.4-mini" if "gpt-5.4-mini" in available else primary
    high = primary
    if route == "micro_patch":
        main = scout if prefer_speed else primary
        return {
            "main_model": main,
            "implementation_model": main,
            "scout_model": scout,
            "review_model": primary,
            "reasoning_effort": "low",
            "fast_mode": prefer_speed and main == "gpt-5.5",
            "fallback_model": "gpt-5.4",
        }
    if gate == "strict" or route in {"risky_feature", "upgrade_or_migration", "research"}:
        return {
            "main_model": high,
            "implementation_model": high,
            "scout_model": scout,
            "review_model": high,
            "reasoning_effort": "high",
            "fast_mode": False,
            "fallback_model": "gpt-5.4",
        }
    return {
        "main_model": primary,
        "implementation_model": primary,
        "scout_model": scout,
        "review_model": primary,
        "reasoning_effort": "medium",
        "fast_mode": False,
        "fallback_model": "gpt-5.4",
    }


def choose_workflow(route: str) -> tuple[list[str], list[str], list[str]]:
    if route == "micro_patch":
        return ["direct-edit", "route-guard", "quality-gate"], [], [
            "context-pack-builder", "pattern-reuse-engine", "parallel-feature-builder", "test-first-synthesizer", "subagent-activation"
        ]
    if route == "clean_reinstall_or_refresh":
        return ["clean-reinstall-manager", "context-indexer", "quality-gate"], ["context-scout"], ["parallel-feature-builder"]
    if route == "research":
        return ["research-radar", "context-indexer", "version-researcher"], ["context-scout", "risk-scout", "docs-memory-reviewer"], []
    if route == "upgrade_or_migration":
        return ["version-researcher", "upgrade-advisor", "plugin-upgrade-migrator", "quality-gate"], ["risk-scout", "dependency-risk-reviewer", "docs-memory-reviewer"], []
    if route == "design_governance":
        return ["design-md-governor", "context-indexer", "style-drift-check", "quality-gate"], ["context-scout", "style-drift-reviewer"], []
    if route == "risky_feature":
        return ["context-indexer", "task-router", "context-pack-builder", "pattern-reuse-engine", "test-first-synthesizer", "parallel-feature-builder", "quality-gate", "merge-readiness"], ["context-scout", "pattern-reuse-scout", "risk-scout", "test-planner", "quality-reviewer"], []
    return ["context-indexer", "task-router", "context-pack-builder", "pattern-reuse-engine", "parallel-feature-builder", "quality-gate", "merge-readiness"], ["context-scout", "pattern-reuse-scout", "test-planner"], []


def choose_context_budget(route: str, gate: str) -> dict[str, Any]:
    if route == "micro_patch":
        return {"max_files": 3, "max_docs": 1, "max_total_chars": 20000, "read_all_initialization_docs": False}
    if gate == "strict":
        return {"max_files": 30, "max_docs": 8, "max_total_chars": 180000, "read_all_initialization_docs": False}
    return {"max_files": 14, "max_docs": 4, "max_total_chars": 80000, "read_all_initialization_docs": False}


def plan(payload: dict[str, Any]) -> dict[str, Any]:
    request = str(payload.get("request") or payload.get("user_request") or "")
    available = set(payload.get("available_models") or ["gpt-5.5", "gpt-5.4", "gpt-5.4-mini"])
    prefer_speed = bool(payload.get("prefer_speed", True))
    route, lane, gate, reasons = detect_route(request, payload)
    skill_sequence, subagents, skipped = choose_workflow(route)
    models = choose_models(route, gate, prefer_speed, available)
    context_budget = choose_context_budget(route, gate)
    if route == "micro_patch":
        subagent_mode = "none"
    elif subagents:
        subagent_mode = "required" if route in {"risky_feature", "upgrade_or_migration", "research"} else "optional"
    else:
        subagent_mode = "none"
    return {
        "status": "planned",
        "runtime_version": "gpt55-auto-orchestration-v1",
        "route": route,
        "lane": lane,
        "quality_gate": gate,
        "reasons": reasons,
        "model_plan": models,
        "context_budget": context_budget,
        "context_retrieval": {
            "first_step": "query_context_index",
            "fallback": "build_context_index",
            "session_brief": ".project-governor/context/SESSION_BRIEF.md",
            "context_index": ".project-governor/context/CONTEXT_INDEX.json",
        },
        "skill_sequence": skill_sequence,
        "subagent_mode": subagent_mode,
        "subagents": subagents,
        "skipped_skills": skipped,
        "quality_rules": {
            "do_not_read_all_initialization_docs": True,
            "do_not_copy_plugin_global_assets": True,
            "run_route_guard_for_micro_patch": route == "micro_patch",
            "run_quality_gate": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Select a GPT-5.5-aware Project Governor runtime plan.")
    parser.add_argument("input", nargs="?")
    parser.add_argument("--request", default="")
    args = parser.parse_args()
    payload = load_payload(args.input) if args.input else {"request": args.request}
    if args.request:
        payload["request"] = args.request
    print(json.dumps(plan(payload), indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
