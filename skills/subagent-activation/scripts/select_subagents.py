#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

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


def infer_mode(data: dict[str, Any]) -> str:
    if data.get("subagent_mode") in {"none", "optional", "required"}:
        return str(data["subagent_mode"])
    workflow = str(data.get("workflow", data.get("skill", "")))
    route = str(data.get("route", ""))
    quality = str(data.get("quality_level", data.get("quality_gate", "")))
    confidence = float(data.get("confidence", 0.7) or 0.7)
    if workflow in {"init-existing-project", "pr-governance-review", "research-radar", "version-researcher"}:
        return "required"
    if route in NO_SUBAGENT_ROUTES and confidence >= 0.85:
        return "none"
    if route in REQUIRED_ROUTES or quality == "strict":
        return "required"
    if route in OPTIONAL_ROUTES:
        return "required" if confidence < 0.7 or data.get("target_is_shared_component") else "optional"
    return "optional"


def selected_for(data: dict[str, Any], mode: str) -> list[str]:
    if mode == "none":
        return []
    workflow = str(data.get("workflow", data.get("skill", "")))
    route = str(data.get("route", ""))
    quality = str(data.get("quality_level", data.get("quality_gate", "")))

    if workflow == "pr-governance-review":
        return ["iteration-compliance-reviewer", "style-drift-reviewer", "architecture-drift-reviewer", "test-planner", "dependency-risk-reviewer", "docs-memory-reviewer"]
    if workflow == "init-existing-project":
        return ["context-scout", "pattern-reuse-scout", "risk-scout", "test-planner", "docs-memory-reviewer"]
    if workflow in {"research-radar", "version-researcher"}:
        return ["context-scout", "risk-scout", "docs-memory-reviewer", "quality-reviewer"]

    agents = ["context-scout"]
    if route not in {"docs_only", "test_only"}:
        agents.append("pattern-reuse-scout")
    if route in {"standard_feature", "risky_feature", "migration", "dependency_upgrade", "refactor"} or quality == "strict":
        agents.append("risk-scout")
    if route not in {"docs_only"}:
        agents.append("test-planner")
    if workflow == "parallel-feature-builder" or route in REQUIRED_ROUTES:
        agents.extend(["implementation-writer", "test-writer", "quality-reviewer"])
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
