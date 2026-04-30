#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SUBAGENT_CONSENT_PHRASE = "I authorize Project Governor to use selected subagents for this task."
SUBAGENT_CONSENT_PHRASES = {
    SUBAGENT_CONSENT_PHRASE.lower(),
    "我授权 Project Governor 使用选定的 subagents",
    "允许 Project Governor 使用选定的 subagents",
}
AUTHORIZATION_FIELDS = ("subagent_authorized", "user_authorized_subagents", "allow_subagents")

AGENTS = {
    "context-scout": {"model": "gpt-5.4-mini", "reasoning": "low", "sandbox": "read-only", "purpose": "find relevant files, entry points, adjacent code, docs, tests, APIs"},
    "pattern-reuse-scout": {"model": "gpt-5.4-mini", "reasoning": "medium", "sandbox": "read-only", "purpose": "find reusable components, hooks, services, schemas, styles, tests"},
    "risk-scout": {"model": "gpt-5.4", "reasoning": "high", "sandbox": "read-only", "purpose": "identify API, schema, dependency, auth, security, migration, data, architecture risks"},
    "test-planner": {"model": "gpt-5.4-mini", "reasoning": "medium", "sandbox": "read-only", "purpose": "plan targeted tests and verification commands"},
    "quality-reviewer": {"model": "gpt-5.4", "reasoning": "high", "sandbox": "read-only", "purpose": "review final patch quality, drift, contracts, and blockers"},
    "implementation-writer": {"model": "gpt-5.4", "reasoning": "medium", "sandbox": "workspace-write", "purpose": "write the smallest approved production patch"},
    "test-writer": {"model": "gpt-5.4-mini", "reasoning": "medium", "sandbox": "workspace-write", "purpose": "write or update tests only"},
    "repair-agent": {"model": "gpt-5.4", "reasoning": "high", "sandbox": "workspace-write", "purpose": "repair failed checks within approved scope"},
    "iteration-compliance-reviewer": {"model": "gpt-5.4-mini", "reasoning": "medium", "sandbox": "read-only", "purpose": "review iteration-first compliance"},
    "style-drift-reviewer": {"model": "gpt-5.4-mini", "reasoning": "medium", "sandbox": "read-only", "purpose": "review style and component drift"},
    "architecture-drift-reviewer": {"model": "gpt-5.4", "reasoning": "high", "sandbox": "read-only", "purpose": "review architecture boundaries and API contracts"},
    "dependency-risk-reviewer": {"model": "gpt-5.4", "reasoning": "high", "sandbox": "read-only", "purpose": "review dependency and upgrade risks"},
    "docs-memory-reviewer": {"model": "gpt-5.4-mini", "reasoning": "medium", "sandbox": "read-only", "purpose": "review docs, memory, ADR/PDR needs"},
}

NO_SUBAGENT_ROUTES = {"micro_patch", "docs_only"}
OPTIONAL_ROUTES = {"tiny_patch", "test_only", "ui_change", "bugfix"}
REQUIRED_ROUTES = {"standard_feature", "risky_feature", "migration", "dependency_upgrade", "refactor"}
REQUIRED_WORKFLOWS = {"init-existing-project", "pr-governance-review", "research-radar", "version-researcher"}
PR_REVIEW_AGENTS = ["iteration-compliance-reviewer", "style-drift-reviewer", "architecture-drift-reviewer", "test-planner", "dependency-risk-reviewer", "docs-memory-reviewer"]
INIT_EXISTING_AGENTS = ["context-scout", "pattern-reuse-scout", "risk-scout", "test-planner", "docs-memory-reviewer"]
RESEARCH_AGENTS = ["context-scout", "risk-scout", "docs-memory-reviewer", "quality-reviewer"]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "authorized", "allowed"}
    return bool(value)


def request_contains_consent_phrase(data: dict[str, Any]) -> bool:
    request = str(data.get("request") or data.get("user_request") or "")
    lower = request.lower()
    return any(phrase in lower or phrase in request for phrase in SUBAGENT_CONSENT_PHRASES)


def subagent_authorized(data: dict[str, Any]) -> bool:
    return any(truthy(data.get(field)) for field in AUTHORIZATION_FIELDS) or request_contains_consent_phrase(data)


def authorization_for(data: dict[str, Any], selected: list[str], mode: str) -> dict[str, Any]:
    spawn_needed = bool(selected)
    authorized = subagent_authorized(data)
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


def explicit_mode_for(data: dict[str, Any]) -> str | None:
    explicit_mode = data.get("subagent_mode")
    return str(explicit_mode) if explicit_mode in {"none", "optional", "required"} else None


def required_mode_for(workflow: str, route: str, quality: str) -> str | None:
    if workflow in REQUIRED_WORKFLOWS:
        return "required"
    if route in REQUIRED_ROUTES or quality == "strict":
        return "required"
    return None


def optional_route_mode(route: str, confidence: float, data: dict[str, Any]) -> str:
    if route in NO_SUBAGENT_ROUTES and confidence >= 0.85:
        return "none"
    if route in OPTIONAL_ROUTES:
        return "required" if confidence < 0.7 or data.get("target_is_shared_component") else "optional"
    return "optional"


def infer_mode(data: dict[str, Any]) -> str:
    explicit_mode = explicit_mode_for(data)
    if explicit_mode:
        return explicit_mode
    workflow = str(data.get("workflow", data.get("skill", "")))
    route = str(data.get("route", ""))
    quality = str(data.get("quality_level", data.get("quality_gate", "")))
    confidence = float(data.get("confidence", 0.7) or 0.7)
    required_mode = required_mode_for(workflow, route, quality)
    return required_mode or optional_route_mode(route, confidence, data)


def workflow_agents(workflow: str) -> list[str] | None:
    if workflow == "pr-governance-review":
        return PR_REVIEW_AGENTS
    if workflow == "init-existing-project":
        return INIT_EXISTING_AGENTS
    if workflow in {"research-radar", "version-researcher"}:
        return RESEARCH_AGENTS
    return None


def base_agents_for(route: str, quality: str, workflow: str) -> list[str]:
    agents = ["context-scout"]
    if route not in {"docs_only", "test_only"}:
        agents.append("pattern-reuse-scout")
    if route in REQUIRED_ROUTES or quality == "strict":
        agents.append("risk-scout")
    if route != "docs_only":
        agents.append("test-planner")
    if workflow == "parallel-feature-builder" or route in REQUIRED_ROUTES:
        agents.extend(["implementation-writer", "test-writer", "quality-reviewer"])
    return agents


def selected_for(data: dict[str, Any], mode: str) -> list[str]:
    if mode == "none":
        return []
    workflow = str(data.get("workflow", data.get("skill", "")))
    route = str(data.get("route", ""))
    quality = str(data.get("quality_level", data.get("quality_gate", "")))

    agents = workflow_agents(workflow) or base_agents_for(route, quality, workflow)
    if data.get("repair_expected"):
        agents.append("repair-agent")
    return unique(agents)


def spawn_instructions(selected: list[str], mode: str) -> str:
    if not selected:
        return "Do not spawn subagents for this route. Continue with direct edit, route-guard, and the required light quality gate."
    lines = [f"Subagent mode: {mode}.", "Explicitly spawn these Project Governor agents and wait for read-only agents before implementation:"]
    for name in selected:
        spec = AGENTS[name]
        lines.append(f"- {name}: {spec['purpose']} (model={spec['model']}, reasoning={spec['reasoning']}, sandbox={spec['sandbox']})")
    lines.append("Consolidate all read-only findings into the task artifact before any write agent modifies production code.")
    lines.append("Only one write agent may modify production code at a time.")
    return "\n".join(lines)


def plan(data: dict[str, Any]) -> dict[str, Any]:
    mode = infer_mode(data)
    selected = selected_for(data, mode)
    skipped = [name for name in AGENTS if name not in selected]
    return {
        "status": "planned",
        "subagent_mode": mode,
        "route": data.get("route"),
        "workflow": data.get("workflow", data.get("skill")),
        "selected_agents": [{"name": name, **AGENTS[name]} for name in selected],
        "skipped_agents": skipped,
        "subagent_authorization": authorization_for(data, selected, mode),
        "model_strategy": {
            "fast_read_only": "gpt-5.4-mini",
            "balanced_default": "gpt-5.4",
            "high_risk_or_final_review": "gpt-5.4 with high reasoning",
            "near_instant_optional": "gpt-5.3-codex-spark only when available and explicitly requested",
        },
        "spawn_instructions": spawn_instructions(selected, mode),
        "wait_policy": "Wait for all read-only subagents before implementation. Do not wait for skipped agents.",
        "write_policy": "Use only one write agent for production code. Test writer may modify tests only. Repair agent is allowed only after quality-gate failure.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Select Project Governor subagents and model strategy.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    print(json.dumps(plan(load(args.input)), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
