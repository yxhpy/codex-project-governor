#!/usr/bin/env python3
from __future__ import annotations

ROLE_RULES = (
    ("agent_instructions", {"exact": ("AGENTS.md",), "path_terms": ("agents.md",)}),
    ("memory", {"path_terms": ("docs/memory", ".project-governor/state")}),
    ("task_history", {"prefixes": ("tasks/",), "path_terms": (".project-governor/state",)}),
    ("governance_history", {"prefixes": ("docs/upgrades/", "docs/research/", "releases/")}),
    ("decision", {"path_terms": ("docs/decisions", "adr", "pdr")}),
    ("architecture", {"path_terms": ("docs/architecture", "architecture")}),
    ("conventions", {"path_terms": ("docs/conventions", "pattern", "component_registry")}),
    ("quality", {"path_terms": ("docs/quality", "quality", "gate")}),
    ("test", {"path_terms": ("test", "spec")}),
    ("ui_or_component", {"path_terms": ("component",), "suffixes": (".tsx", ".jsx", ".vue", ".svelte")}),
    ("api", {"path_terms": ("api", "route", "controller"), "sample_terms": ("endpoint",)}),
    ("data_model", {"path_terms": ("schema", "model", "migration")}),
    ("design", {"exact": ("DESIGN.md",), "path_terms": ("design", "token")}),
    ("auth", {"path_or_sample_terms": ("auth", "oauth", "session", "permission", "rbac", "login")}),
    ("payment", {"path_or_sample_terms": ("payment", "billing", "invoice", "refund", "checkout")}),
)
SECURITY_TERMS = ("secret", "token", "password", "private key")
CORE_BRIEF_ROLES = {
    "agent_instructions",
    "conventions",
    "quality",
    "memory",
    "decision",
    "architecture",
    "task_history",
    "governance_history",
    "design",
}
SESSION_POLICY_LINES = [
    "",
    "## Policy",
    "",
    "- Do not read all initialization documents unless the context query is insufficient.",
    "- Read `.project-governor/context/DOCS_MANIFEST.json` before deciding which large docs to open.",
    "- Prefer `recommended_sections` line ranges from context queries before opening full documents.",
    "- At session start, run memory-search for prior command failures, repeated mistakes, stale-memory notes, decisions, and task history related to the request.",
    "- Prefer task-specific retrieval from `.project-governor/context/CONTEXT_INDEX.json`.",
    "- Treat stale or superseded docs as avoid-by-default unless the task is explicitly about cleanup or history.",
    "- Start non-trivial work with `.project-governor/state/SESSION.json`; finish with evidence and `record_session_learning.py` for failed commands or stale memories.",
    "- Use fast read-only scouting for retrieval and high-reasoning models for implementation/review when available.",
]


def role_rule_matches(rel: str, low: str, sample: str, rule: dict[str, tuple[str, ...]]) -> bool:
    return (
        rel in rule.get("exact", ())
        or low.startswith(rule.get("prefixes", ()))
        or rel.endswith(rule.get("suffixes", ()))
        or any(term in low for term in rule.get("path_terms", ()))
        or any(term in sample for term in rule.get("sample_terms", ()))
        or any(term in low or term in sample for term in rule.get("path_or_sample_terms", ()))
    )


def default_roles(rel: str, roles: list[str]) -> list[str]:
    if roles:
        return roles
    return ["doc"] if rel.endswith(".md") else ["code"]


def role_for(rel: str, text: str, sensitive: bool = False) -> list[str]:
    low = rel.lower()
    sample = text.lower()
    roles = [role for role, rule in ROLE_RULES if role_rule_matches(rel, low, sample, rule)]
    if sensitive or any(term in sample for term in SECURITY_TERMS):
        roles.append("security")
    return sorted(set(default_roles(rel, roles)))


def session_brief_header(index: dict) -> list[str]:
    return [
        "# Project Governor Harness v6 Session Brief",
        "",
        "Use this brief before reading large project docs. Query CONTEXT_INDEX.json for task-specific files.",
        "",
        f"Schema: `{index['schema']}`",
        f"Indexed files: {index['entry_count']}",
        f"Git head: `{index.get('git', {}).get('head') or 'unknown'}`",
        f"Dirty working tree: `{index.get('git', {}).get('dirty')}`",
        "",
        "## Core references",
        "",
    ]


def core_reference_entries(index: dict) -> list[dict]:
    return [
        entry
        for entry in index["entries"]
        if any(role in entry["roles"] for role in CORE_BRIEF_ROLES)
    ]


def core_reference_lines(core: list[dict]) -> list[str]:
    lines: list[str] = []
    for entry in core[:25]:
        suffix = " sensitive" if entry.get("sensitive") else ""
        lines.append(f"- `{entry['path']}` — {', '.join(entry['roles'])}{suffix}")
    return lines


def session_brief(index: dict) -> str:
    lines = session_brief_header(index)
    lines.extend(core_reference_lines(core_reference_entries(index)))
    lines.extend(SESSION_POLICY_LINES)
    return "\n".join(lines) + "\n"
