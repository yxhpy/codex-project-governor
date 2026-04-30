#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TASK_ROUTER = ROOT / "skills" / "task-router" / "scripts" / "classify_task.py"
SUBAGENT_CONSENT_PHRASE = "I authorize Project Governor to use selected subagents for this task."
SUBAGENT_CONSENT_PHRASES = {
    SUBAGENT_CONSENT_PHRASE.lower(),
    "我授权 Project Governor 使用选定的 subagents",
    "允许 Project Governor 使用选定的 subagents",
}
AUTHORIZATION_FIELDS = ("subagent_authorized", "user_authorized_subagents", "allow_subagents")
EXECUTION_POLICY_PATH = ".project-governor/runtime/EXECUTION_POLICY.json"


def load_payload(path: str | None, request: str | None = None) -> dict[str, Any]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    if request:
        return {"request": request}
    raw = sys.stdin.read().strip()
    if not raw:
        raise SystemExit("Provide an input JSON file, --request, or JSON on stdin.")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"request": raw}
    return data if isinstance(data, dict) else {"request": str(data)}


def load_task_router() -> Any:
    spec = importlib.util.spec_from_file_location("project_governor_task_router", TASK_ROUTER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import task router: {TASK_ROUTER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "authorized", "allowed"}
    return bool(value)


def request_contains_consent_phrase(payload: dict[str, Any]) -> bool:
    request = str(payload.get("request") or payload.get("user_request") or "")
    lower = request.lower()
    return any(phrase in lower or phrase in request for phrase in SUBAGENT_CONSENT_PHRASES)


def subagent_authorized(payload: dict[str, Any]) -> bool:
    return any(truthy(payload.get(field)) for field in AUTHORIZATION_FIELDS) or request_contains_consent_phrase(payload)


def subagent_authorization(payload: dict[str, Any], subagents: list[str], mode: str) -> dict[str, Any]:
    spawn_needed = bool(subagents)
    authorized = subagent_authorized(payload)
    if not spawn_needed:
        status = "not_required"
        reason = "No subagents are selected for this route."
    elif authorized:
        status = "authorized"
        reason = "The request or input explicitly authorized Project Governor subagent spawning."
    else:
        status = "needs_explicit_user_authorization"
        reason = "Host runtimes may require the user to explicitly authorize subagent spawning even when Project Governor selects subagents automatically."
    return {
        "status": status,
        "subagent_mode": mode,
        "spawn_requires_user_authorization": spawn_needed,
        "authorized": authorized if spawn_needed else False,
        "consent_phrase": SUBAGENT_CONSENT_PHRASE if spawn_needed else "",
        "accepted_input_fields": list(AUTHORIZATION_FIELDS),
        "reason": reason,
    }


def classify(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("status") == "classified" and payload.get("router_version"):
        return payload
    module = load_task_router()
    merged = dict(payload)
    if "request" not in merged and "user_request" in merged:
        merged["request"] = merged["user_request"]
    return module.classify(merged)


def normalized_route(route: str) -> str:
    if route == "dependency_upgrade":
        return "upgrade_or_migration"
    return route


def choose_models(route: str, gate: str, prefer_speed: bool, available: set[str]) -> dict[str, Any]:
    primary = "gpt-5.5" if "gpt-5.5" in available else "gpt-5.4"
    scout = "gpt-5.4-mini" if "gpt-5.4-mini" in available else primary
    if route in {"micro_patch", "docs_only"}:
        main = scout if prefer_speed else primary
        return {
            "main_model": main,
            "implementation_model": main,
            "scout_model": scout,
            "review_model": primary,
            "reasoning_effort": "low",
            "fast_mode": prefer_speed and main == scout,
            "fallback_model": "gpt-5.4",
        }
    if gate == "strict" or route in {"risky_feature", "upgrade_or_migration", "research", "refactor"}:
        return {
            "main_model": primary,
            "implementation_model": primary,
            "scout_model": scout,
            "review_model": primary,
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


def choose_context_budget(route: str, gate: str, confidence: float) -> dict[str, Any]:
    if route == "micro_patch":
        return {"max_files": 3, "max_docs": 1, "max_sections": 3, "max_total_chars": 20_000, "read_all_initialization_docs": False}
    if route in {"research", "upgrade_or_migration"}:
        return {"max_files": 36, "max_docs": 12, "max_sections": 18, "max_total_chars": 220_000, "read_all_initialization_docs": False}
    if gate == "strict":
        return {"max_files": 30, "max_docs": 8, "max_sections": 16, "max_total_chars": 180_000, "read_all_initialization_docs": False}
    if confidence < 0.70:
        return {"max_files": 20, "max_docs": 6, "max_sections": 12, "max_total_chars": 110_000, "read_all_initialization_docs": False}
    return {"max_files": 14, "max_docs": 4, "max_sections": 10, "max_total_chars": 80_000, "read_all_initialization_docs": False}


def subagents_for(route: str, mode: str) -> list[str]:
    if mode == "none":
        return []
    base = ["context-scout", "pattern-reuse-scout", "test-planner"]
    if route in {"risky_feature", "upgrade_or_migration", "refactor"}:
        base.extend(["risk-scout", "quality-reviewer"])
    if route == "research":
        base.extend(["risk-scout", "docs-memory-reviewer"])
    return list(dict.fromkeys(base))


UPGRADE_SEQUENCE = [
    "session-lifecycle",
    "version-researcher",
    "upgrade-advisor",
    "plugin-upgrade-migrator",
    "test-first-synthesizer",
    "engineering-standards-governor",
    "quality-gate",
    "evidence-manifest",
    "merge-readiness",
]


def insert_before(seq: list[str], item: str, before: str) -> None:
    if item in seq:
        return
    index = seq.index(before) if before in seq else len(seq)
    seq.insert(index, item)


def session_required(route: str) -> bool:
    return route not in {"micro_patch", "docs_only", "clean_reinstall_or_refresh"}


def skill_sequence_from(classification: dict[str, Any], route: str) -> list[str]:
    seq = list(classification.get("required_workflow") or [])
    if route == "upgrade_or_migration":
        seq = list(UPGRADE_SEQUENCE)
    if route == "standard_feature":
        insert_before(seq, "test-first-synthesizer", "parallel-feature-builder")
    if classification.get("evidence_required"):
        insert_before(seq, "evidence-manifest", "merge-readiness")
    if session_required(route) and "session-lifecycle" not in seq:
        seq.insert(0, "session-lifecycle")
    return seq


def skipped_skills(classification: dict[str, Any], route: str) -> list[str]:
    skipped = list(classification.get("skipped_workflow") or [])
    if route == "micro_patch":
        skipped.extend(["session-lifecycle", "evidence-manifest", "harness-doctor"])
    return sorted(set(skipped))


def apply_budget_gate(context_budget: dict[str, Any], route_doc_pack: dict[str, Any]) -> None:
    budget_gate = route_doc_pack.get("context_budget_gate", {}) if isinstance(route_doc_pack, dict) else {}
    if not budget_gate:
        return
    context_budget["max_docs"] = min(context_budget["max_docs"], int(budget_gate.get("max_initial_docs", context_budget["max_docs"])))
    context_budget["max_sections"] = min(context_budget.get("max_sections", 12), int(budget_gate.get("max_sections", context_budget.get("max_sections", 12))))
    context_budget["max_total_chars_first"] = int(budget_gate.get("max_total_chars_first", context_budget["max_total_chars"]))
    context_budget["full_doc_requires_reason"] = bool(budget_gate.get("full_doc_requires_reason", True))


def normalized_subagent_mode(classification: dict[str, Any], route: str) -> str:
    subagent_mode = str(classification.get("subagent_mode", "optional"))
    if route in {"standard_feature", "risky_feature", "upgrade_or_migration", "research", "refactor"} and subagent_mode == "optional":
        return "required"
    return subagent_mode


def route_pack_value(route_doc_pack: dict[str, Any], key: str, default: Any) -> Any:
    if isinstance(route_doc_pack, dict):
        return route_doc_pack.get(key, default)
    return default


def context_retrieval_policy(route: str, route_doc_pack: dict[str, Any]) -> dict[str, Any]:
    default_compression = {
        "strategy": "query_aware_section_excerpts",
        "prefer_section_summary": True,
        "defer_full_documents": True,
    }
    return {
        "first_step": "read_docs_manifest_then_query_context_index_v2",
        "memory_search_first_step": "query_context_index_v2_memory_search",
        "fallback": "build_context_index_v2",
        "docs_manifest": ".project-governor/context/DOCS_MANIFEST.json",
        "session_brief": ".project-governor/context/SESSION_BRIEF.md",
        "context_index": ".project-governor/context/CONTEXT_INDEX.json",
        "query_granularity": "section",
        "read_order": route_pack_value(route_doc_pack, "read_order", []),
        "stale_doc_filter": {
            "exclude_statuses_by_default": ["stale", "superseded"],
            "include_only_when_requested": True,
        },
        "compression": route_doc_pack.get("compression", default_compression) if isinstance(route_doc_pack, dict) else {},
        "startup_memory_search": route not in {"micro_patch", "docs_only"},
        "read_all_initialization_docs": False,
    }


def state_policy(route: str) -> dict[str, Any]:
    session_required = route not in {"micro_patch", "docs_only"}
    return {
        "state_dir": ".project-governor/state",
        "session_start": session_required,
        "session_end": session_required,
        "command_learning_ledger": ".project-governor/state/COMMAND_LEARNINGS.json",
        "memory_hygiene_ledger": ".project-governor/state/MEMORY_HYGIENE.json",
        "one_active_feature_per_session": True,
        "collision_detection": True,
    }


def memory_policy(route: str) -> dict[str, Any]:
    memory_required = route not in {"micro_patch", "docs_only"}
    return {
        "startup_memory_search_required": memory_required,
        "startup_memory_search_command": "python3 skills/context-indexer/scripts/query_context_index.py --project . --request <task-request> --memory-search --auto-build --format text",
        "record_session_learning_required": memory_required,
        "learning_recorder": "skills/memory-compact/scripts/record_session_learning.py",
        "failed_commands_target": ".project-governor/state/COMMAND_LEARNINGS.json",
        "repeated_mistakes_target": "docs/memory/REPEATED_AGENT_MISTAKES.md",
        "stale_memory_target": ".project-governor/state/MEMORY_HYGIENE.json",
    }


def evidence_policy(evidence_required: bool, gate: str, route: str) -> dict[str, Any]:
    return {
        "required": evidence_required,
        "manifest": ".project-governor/evidence/<task-id>/EVIDENCE.json",
        "acceptance_mapping_required": evidence_required,
        "commands_required": gate in {"standard", "strict"} and route != "docs_only",
    }


def task_request_text(payload: dict[str, Any], classification: dict[str, Any]) -> str:
    pieces = [
        str(payload.get("request", payload.get("user_request", ""))),
        str(classification.get("request", "")),
        " ".join(map(str, payload.get("constraints", []))) if isinstance(payload.get("constraints"), list) else "",
    ]
    return " ".join(pieces).lower()


def explicit_execution_context(payload: dict[str, Any]) -> str:
    raw = payload.get("execution_context")
    if isinstance(raw, dict):
        context = raw.get("type", raw.get("context", raw.get("task_type", "")))
        return str(context)
    if isinstance(raw, str):
        return raw
    return ""


def infer_execution_context(payload: dict[str, Any], classification: dict[str, Any]) -> str:
    explicit = explicit_execution_context(payload)
    if explicit:
        return explicit
    text = task_request_text(payload, classification)
    release_signal = bool(re.search(r"\b(release|publish|tag|ship)\b|发布|发版|打标签", text, flags=re.IGNORECASE))
    gh_signal = bool(re.search(r"\b(gh|github cli|github api)\b", text, flags=re.IGNORECASE))
    publish_signal = bool(re.search(r"\b(release pipeline|publish pipeline|create release)\b|发布流水线", text, flags=re.IGNORECASE))
    if release_signal and (gh_signal or publish_signal):
        return "release_publish"
    return ""


def execution_policy(payload: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    context = infer_execution_context(payload, classification)
    required = bool(context)
    return {
        "required": required,
        "context": context,
        "policy_path": EXECUTION_POLICY_PATH if required else "",
        "quality_gate_input": {"execution_context": context, "execution_policy_path": EXECUTION_POLICY_PATH} if required else {},
        "record_commands_required": required,
        "record_constraint_in_plan": required,
        "override_field": "execution_policy_override_approved" if required else "",
    }


def quality_rules(route: str, evidence_required: bool, execution_policy_required: bool = False) -> dict[str, Any]:
    return {
        "do_not_read_all_initialization_docs": True,
        "do_not_copy_plugin_global_assets": True,
        "run_route_guard": True,
        "run_execution_policy": execution_policy_required,
        "run_engineering_standards": route not in {"micro_patch", "docs_only", "clean_reinstall_or_refresh"},
        "route_guard_uses_git_diff_facts": True,
        "run_quality_gate": True,
        "record_failed_commands_before_final": True,
        "classify_stale_memory_before_final": True,
        "require_evidence_manifest": evidence_required,
        "standard_feature_requires_test_first": True,
        "enforce_context_budget_gate": True,
        "prefer_section_ranges_before_full_docs": True,
    }


def plan(payload: dict[str, Any]) -> dict[str, Any]:
    available = set(payload.get("available_models") or ["gpt-5.5", "gpt-5.4", "gpt-5.4-mini"])
    prefer_speed = bool(payload.get("prefer_speed", True))
    classification = classify(payload)
    route = normalized_route(str(classification["route"]))
    gate = str(classification.get("quality_gate") or classification.get("quality_level") or "standard")
    confidence = float(classification.get("confidence", 0.55))
    model_plan = choose_models(route, gate, prefer_speed, available)
    context_budget = choose_context_budget(route, gate, confidence)
    route_doc_pack = classification.get("route_doc_pack", {})
    apply_budget_gate(context_budget, route_doc_pack)
    subagent_mode = normalized_subagent_mode(classification, route)
    subagents = subagents_for(route, subagent_mode)
    sequence = skill_sequence_from(classification, route)
    evidence_required = bool(classification.get("evidence_required"))
    execution_policy_plan = execution_policy(payload, classification)

    return {
        "status": "planned",
        "runtime_version": "project-governor-harness-v6",
        "router_version": classification.get("router_version"),
        "route": route,
        "lane": classification.get("lane", "standard_lane"),
        "quality_gate": gate,
        "confidence": confidence,
        "risk_score": classification.get("risk_score", 0.0),
        "intent": classification.get("intent", "unknown"),
        "evidence_required": evidence_required,
        "reasons": classification.get("reasons", []),
        "classification": classification,
        "model_plan": model_plan,
        "context_budget": context_budget,
        "route_doc_pack": route_doc_pack,
        "context_retrieval": context_retrieval_policy(route, route_doc_pack),
        "state_policy": state_policy(route),
        "memory_policy": memory_policy(route),
        "evidence_policy": evidence_policy(evidence_required, gate, route),
        "execution_policy": execution_policy_plan,
        "skill_sequence": sequence,
        "subagent_mode": subagent_mode,
        "subagents": subagents,
        "subagent_authorization": subagent_authorization(payload, subagents, subagent_mode),
        "skipped_skills": skipped_skills(classification, route),
        "quality_rules": quality_rules(route, evidence_required, bool(execution_policy_plan.get("required"))),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Select a Project Governor Harness v6.1 runtime plan.")
    parser.add_argument("input", nargs="?")
    parser.add_argument("--request", default="")
    args = parser.parse_args()
    payload = load_payload(args.input, args.request or None)
    if args.request:
        payload["request"] = args.request
    print(json.dumps(plan(payload), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
