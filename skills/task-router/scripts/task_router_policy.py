#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from task_router_config import DOC_PACKS

STRICT_SUBAGENT_ROUTES = {"standard_feature", "risky_feature", "refactor", "dependency_upgrade", "upgrade_or_migration", "research"}
CONDITIONAL_SUBAGENT_ROUTES = STRICT_SUBAGENT_ROUTES | {"ui_change", "bugfix"}
NO_SUBAGENT_IF_CONFIDENT = {"docs_only", "test_only", "clean_reinstall_or_refresh"}
NEGATIVE_GUARD_OVERRIDES = {
    "do_not_change_api": {"allow_api_changes": False},
    "do_not_change_schema": {"allow_schema_changes": False},
    "do_not_add_files": {"max_added_files": 0},
    "do_not_add_dependencies": {"allow_dependencies": False},
    "do_not_change_global_style": {"allow_global_style_changes": False},
    "do_not_change_shared_components": {"allow_shared_component_changes": False},
}


def route_budget(route: str, lane: str) -> dict[str, Any]:
    if route == "micro_patch":
        return {
            "max_files_changed": 1,
            "max_new_files": 0,
            "allow_dependencies": False,
            "allow_public_contract_changes": False,
            "allow_schema_changes": False,
            "allow_refactor": False,
            "allow_global_style_changes": False,
            "allow_shared_component_changes": False,
            "allow_new_components": False,
            "requires_adr_or_pdr": False,
        }
    if route in {"dependency_upgrade", "upgrade_or_migration"}:
        return {
            "max_files_changed": 8,
            "max_new_files": 3,
            "allow_dependencies": True,
            "allow_public_contract_changes": False,
            "allow_schema_changes": False,
            "allow_refactor": False,
            "requires_adr_or_pdr": True,
        }
    if lane == "fast_lane":
        return {"max_files_changed": 3, "max_new_files": 1, "allow_dependencies": False, "allow_public_contract_changes": False, "allow_schema_changes": False}
    if lane == "risk_lane":
        return {"max_files_changed": 10, "max_new_files": 4, "allow_dependencies": False, "allow_public_contract_changes": True, "allow_schema_changes": True, "requires_adr_or_pdr": True}
    if lane == "refactor_lane":
        return {"max_files_changed": 12, "max_new_files": 2, "allow_dependencies": False, "allow_public_contract_changes": False, "allow_schema_changes": False, "allow_refactor": True, "requires_adr_or_pdr": True}
    return {"max_files_changed": 8, "max_new_files": 3, "allow_dependencies": False, "allow_public_contract_changes": False, "allow_schema_changes": False}


def base_route_guard(route: str, budget: dict[str, Any], negative_constraints: list[str]) -> dict[str, Any]:
    return {
        "route": route,
        "max_modified_files": budget.get("max_files_changed", 9999),
        "max_added_files": budget.get("max_new_files", 9999),
        "allow_dependencies": bool(budget.get("allow_dependencies", False)),
        "allow_api_changes": bool(budget.get("allow_public_contract_changes", False)),
        "allow_schema_changes": bool(budget.get("allow_schema_changes", False)),
        "allow_new_components": bool(budget.get("allow_new_components", True)),
        "allow_global_style_changes": bool(budget.get("allow_global_style_changes", True)),
        "allow_shared_component_changes": bool(budget.get("allow_shared_component_changes", True)),
        "allow_rewrite": bool(budget.get("allow_refactor", False)),
        "max_repair_rounds": 3,
        "negative_constraints": negative_constraints,
        "must_stop_if_budget_exceeded": True,
    }


def apply_negative_guardrails(guard: dict[str, Any], negative_constraints: list[str]) -> dict[str, Any]:
    for constraint in negative_constraints:
        guard.update(NEGATIVE_GUARD_OVERRIDES.get(constraint, {}))
    return guard


def route_guard_requirements(route: str, budget: dict[str, Any], negative_constraints: list[str]) -> dict[str, Any]:
    return apply_negative_guardrails(base_route_guard(route, budget, negative_constraints), negative_constraints)


def route_doc_pack(route: str, quality: str) -> dict[str, Any]:
    config = dict(DOC_PACKS.get(route, DOC_PACKS["standard_feature"]))
    if quality == "strict":
        config["max_initial_docs"] = max(config["max_initial_docs"], 6)
        config["max_sections"] = max(config["max_sections"], 14)
    return {
        "id": f"{route}_doc_pack",
        "route": route,
        "primary_roles": config["primary_roles"],
        "read_order": [
            ".project-governor/context/DOCS_MANIFEST.json",
            ".project-governor/context/SESSION_BRIEF.md",
            "memory_search" if config["memory_search"] else "skip_memory_search_for_route",
            "query_context_index.recommended_sections",
            "full_documents_only_if_sections_insufficient",
        ],
        "context_budget_gate": {
            "max_initial_docs": config["max_initial_docs"],
            "max_sections": config["max_sections"],
            "max_total_chars_first": config["max_total_chars_first"],
            "full_doc_requires_reason": True,
            "exclude_doc_statuses_by_default": ["stale", "superseded"],
        },
        "compression": {"strategy": "query_aware_section_excerpts", "prefer_section_summary": True, "defer_full_documents": True},
        "escalate_to_full_docs_if": [
            "context_index_missing_or_stale",
            "query_confidence_below_threshold",
            "public_contract_or_template_path_change_requires_source_of_truth",
            "section_excerpt_conflicts_with_adjacent_code",
        ],
    }


WORKFLOWS: dict[str, tuple[list[str], list[str]]] = {
    "micro_patch": (
        ["direct-edit", "route-guard", "quality-gate", "evidence-manifest-lite"],
        ["context-pack-builder", "pattern-reuse-engine", "parallel-feature-builder", "test-first-synthesizer", "subagent-activation", "subagent-audit"],
    ),
    "clean_reinstall_or_refresh": (["clean-reinstall-manager", "context-indexer", "harness-doctor", "quality-gate"], ["parallel-feature-builder"]),
    "research": (["session-lifecycle", "research-radar", "context-indexer", "version-researcher", "evidence-manifest"], []),
    "dependency_upgrade": (["session-lifecycle", "version-researcher", "upgrade-advisor", "plugin-upgrade-migrator", "test-first-synthesizer", "engineering-standards-governor", "quality-gate", "evidence-manifest", "merge-readiness"], []),
    "upgrade_or_migration": (["session-lifecycle", "version-researcher", "upgrade-advisor", "plugin-upgrade-migrator", "test-first-synthesizer", "engineering-standards-governor", "quality-gate", "evidence-manifest", "merge-readiness"], []),
    "docs_only": (["direct-edit", "quality-gate", "merge-readiness"], ["parallel-feature-builder", "subagent-audit", "test-first-synthesizer"]),
    "test_only": (["context-indexer", "context-pack-builder", "direct-edit", "engineering-standards-governor", "quality-gate", "evidence-manifest", "merge-readiness"], ["parallel-feature-builder"]),
    "risky_feature": (["session-lifecycle", "context-indexer", "context-pack-builder", "pattern-reuse-engine", "test-first-synthesizer", "parallel-feature-builder", "engineering-standards-governor", "quality-gate", "evidence-manifest", "merge-readiness"], []),
    "refactor": (["session-lifecycle", "context-indexer", "context-pack-builder", "pattern-reuse-engine", "test-first-synthesizer", "parallel-feature-builder", "architecture-drift-check", "engineering-standards-governor", "quality-gate", "evidence-manifest", "merge-readiness"], []),
}
DEFAULT_WORKFLOW = (["session-lifecycle", "context-indexer", "context-pack-builder", "pattern-reuse-engine", "test-first-synthesizer", "parallel-feature-builder", "engineering-standards-governor", "quality-gate", "evidence-manifest", "merge-readiness"], [])


def workflow(route: str) -> tuple[list[str], list[str]]:
    required, skipped = WORKFLOWS.get(route, DEFAULT_WORKFLOW)
    return list(required), list(skipped)


def workflow_skills(items: list[str]) -> list[str]:
    skills: list[str] = []
    aliases = {"direct-edit": None, "evidence-manifest-lite": "evidence-manifest"}
    for item in items:
        item = aliases.get(item, item)
        if not item:
            continue
        if item.endswith("-quality-gate"):
            item = "quality-gate"
        if item not in skills:
            skills.append(item)
    return skills


def subagent_mode(route: str, quality: str, confidence: float, shared_or_global: bool) -> str:
    if route == "micro_patch" and confidence >= 0.82 and not shared_or_global:
        return "none"
    if route in NO_SUBAGENT_IF_CONFIDENT:
        return "optional" if confidence < 0.70 else "none"
    if route in CONDITIONAL_SUBAGENT_ROUTES:
        return "required" if quality == "strict" or confidence < 0.85 or route in STRICT_SUBAGENT_ROUTES else "optional"
    return "optional"


def evidence_required_for(route: str, quality: str) -> bool:
    return route not in {"micro_patch", "docs_only", "clean_reinstall_or_refresh"} or quality == "strict"


def escalations_for(evidence_required: bool, quality: str) -> list[str]:
    escalations = [
        "modified files exceed route budget",
        "new files added when not allowed",
        "shared/global component changed unexpectedly",
        "public API, schema, dependency, or style-system change required",
        "rewrite threshold exceeded",
        "quality gate fails after repair-loop limit",
    ]
    if evidence_required:
        escalations.append("evidence manifest is missing or incomplete")
    if quality in {"standard", "strict"}:
        escalations.append("tests cannot validate the change")
    return escalations
