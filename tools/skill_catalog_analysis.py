from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from skill_catalog_validation import find_issues, issue, parse_frontmatter
except ModuleNotFoundError:  # pragma: no cover - supports package-style imports.
    from tools.skill_catalog_validation import find_issues, issue, parse_frontmatter

SCHEMA = "project-governor-skill-catalog-analysis-v1"
PUBLIC_VISIBILITIES = {"primary", "workflow", "advanced"}
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9-]{2,}")
STOP_WORDS = {
    "and", "are", "before", "code", "codex", "for", "from", "governor", "into", "project", "projects",
    "skill", "skills", "that", "the", "this", "when", "with", "work", "workflow", "workflows",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tokenize(*values: str) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        for token in TOKEN_RE.findall(value.lower().replace("_", "-")):
            for part in token.split("-"):
                if part and part not in STOP_WORDS and len(part) >= 3:
                    tokens.add(part)
    return tokens


def overlap_score(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return round(len(left & right) / min(len(left), len(right)), 3)


def skill_dirs(project: Path) -> set[str]:
    skills_dir = project / "skills"
    if not skills_dir.exists():
        return set()
    return {path.name for path in skills_dir.iterdir() if path.is_dir()}


def build_skill_rows(project: Path, catalog_entries: list[dict[str, Any]], actual_names: set[str]) -> dict[str, dict[str, Any]]:
    entries_by_name = {str(entry.get("name")): entry for entry in catalog_entries if entry.get("name")}
    rows: dict[str, dict[str, Any]] = {}
    for name in sorted(actual_names | set(entries_by_name)):
        entry = entries_by_name.get(name, {})
        metadata = parse_frontmatter(project / "skills" / name / "SKILL.md")
        description = metadata.get("description", "")
        summary = str(entry.get("summary", ""))
        rows[name] = {
            "name": name,
            "visibility": entry.get("visibility"),
            "category": entry.get("category"),
            "summary": summary,
            "description": description,
            "frontmatter_name": metadata.get("name"),
            "has_scripts": (project / "skills" / name / "scripts").exists(),
            "tokens": sorted(tokenize(name, summary, description)),
        }
    return rows


def public_group_candidates(rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows.values():
        if row.get("visibility") in PUBLIC_VISIBILITIES and row.get("category"):
            by_category[str(row["category"])].append(row)

    candidates: list[dict[str, Any]] = []
    for category, items in sorted(by_category.items()):
        if len(items) < 2:
            continue
        skills = [str(item["name"]) for item in sorted(items, key=lambda item: str(item["name"]))]
        candidates.append(
            {
                "type": "category_umbrella",
                "category": category,
                "skills": skills,
                "recommendation": "consolidate_public_docs_or_use_one_workflow_entry",
                "confidence": "medium",
                "rationale": "Multiple public-facing skills share a category; keep implementations but prefer one grouped user-facing entry.",
            }
        )
    return candidates


def quality_facet_candidates(rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    quality = [row for row in rows.values() if row.get("category") == "quality" and row.get("visibility") in {"internal", "advanced"}]
    if len(quality) < 3:
        return []
    return [
        {
            "type": "quality_gate_facets",
            "category": "quality",
            "skills": [str(row["name"]) for row in sorted(quality, key=lambda item: str(item["name"]))],
            "recommendation": "keep_as_quality_gate_facets_not_primary_entries",
            "confidence": "high",
            "rationale": "Many quality skills are checks or diagnostics that should usually be invoked through quality-gate.",
        }
    ]


def overlap_candidates(rows: dict[str, dict[str, Any]], min_overlap: float) -> list[dict[str, Any]]:
    names = sorted(rows)
    candidates: list[dict[str, Any]] = []
    for index, left_name in enumerate(names):
        left = rows[left_name]
        left_tokens = set(left["tokens"])
        for right_name in names[index + 1 :]:
            right = rows[right_name]
            right_tokens = set(right["tokens"])
            score = overlap_score(left_tokens, right_tokens)
            if score < min_overlap:
                continue
            shared = sorted(left_tokens & right_tokens)
            if len(shared) < 3:
                continue
            candidates.append(
                {
                    "type": "term_overlap",
                    "skills": [left_name, right_name],
                    "score": score,
                    "shared_terms": shared[:12],
                    "recommendation": "review_for_documentation_consolidation_or_clearer_boundaries",
                    "confidence": "low" if score < 0.5 else "medium",
                }
            )
    return sorted(candidates, key=lambda item: (-float(item["score"]), item["skills"]))


def load_catalog(project: Path) -> tuple[Path, dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    catalog_path = project / "skills" / "CATALOG.json"
    if not catalog_path.exists():
        missing = issue("error", "missing_catalog_file", "skills/CATALOG.json does not exist.", path=str(catalog_path))
        return catalog_path, {"schema": None, "skills": []}, [], [missing]

    catalog = read_json(catalog_path)
    entries = catalog.get("skills", [])
    if not isinstance(entries, list):
        entries = []
    dict_entries = [entry for entry in entries if isinstance(entry, dict)]
    return catalog_path, catalog, dict_entries, []


def build_consolidation_candidates(rows: dict[str, dict[str, Any]], min_overlap: float) -> list[dict[str, Any]]:
    candidates = public_group_candidates(rows)
    candidates.extend(quality_facet_candidates(rows))
    candidates.extend(overlap_candidates(rows, min_overlap))
    return candidates


def resolved_consolidation_groups(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    groups = catalog.get("consolidation_groups", [])
    if not isinstance(groups, list):
        return []
    return [group for group in groups if isinstance(group, dict) and group.get("status") == "resolved"]


def group_matches_candidate(group: dict[str, Any], candidate: dict[str, Any]) -> bool:
    candidate_types = group.get("candidate_types", [])
    if candidate_types and candidate.get("type") not in set(candidate_types):
        return False
    group_skills = set(group.get("skills", []))
    candidate_skills = set(candidate.get("skills", []))
    return bool(candidate_skills) and candidate_skills.issubset(group_skills)


def split_resolved_candidates(
    candidates: list[dict[str, Any]], groups: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    open_candidates: list[dict[str, Any]] = []
    resolved: list[dict[str, Any]] = []
    for candidate in candidates:
        match = next((group for group in groups if group_matches_candidate(group, candidate)), None)
        if not match:
            open_candidates.append(candidate)
            continue
        resolved_item = dict(candidate)
        resolved_item["resolved_by"] = match.get("name")
        resolved_item["entrypoint"] = match.get("entrypoint")
        resolved_item["resolution"] = match.get("resolution")
        resolved.append(resolved_item)
    return open_candidates, resolved


def value_counts(rows: dict[str, dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get(key)) for row in rows.values()).items()))


def analysis_status(issues: list[dict[str, Any]]) -> str:
    if any(item["severity"] == "error" for item in issues):
        return "fail"
    if issues:
        return "warn"
    return "pass"


def analysis_summary(
    issues: list[dict[str, Any]], candidates: list[dict[str, Any]], resolved: list[dict[str, Any]], rows: dict[str, dict[str, Any]]
) -> dict[str, int]:
    return {
        "blocking_issue_count": sum(1 for item in issues if item["severity"] == "error"),
        "warning_count": sum(1 for item in issues if item["severity"] != "error"),
        "candidate_count": len(candidates),
        "resolved_consolidation_count": len(resolved),
        "public_skill_count": sum(1 for row in rows.values() if row.get("visibility") in PUBLIC_VISIBILITIES),
        "internal_skill_count": sum(1 for row in rows.values() if row.get("visibility") == "internal"),
    }


def analyze(project: Path, min_overlap: float) -> dict[str, Any]:
    catalog_path, catalog, entries, preflight_issues = load_catalog(project)
    actual_names = skill_dirs(project)
    rows = build_skill_rows(project, entries, actual_names)
    issues = preflight_issues + find_issues(project, catalog, entries, actual_names)
    raw_candidates = build_consolidation_candidates(rows, min_overlap)
    candidates, resolved = split_resolved_candidates(raw_candidates, resolved_consolidation_groups(catalog))
    return {
        "schema": SCHEMA,
        "status": analysis_status(issues),
        "project": str(project),
        "catalog_path": str(catalog_path),
        "skill_count": len(actual_names),
        "catalog_entry_count": len(entries),
        "visibility_counts": value_counts(rows, "visibility"),
        "category_counts": value_counts(rows, "category"),
        "issues": issues,
        "consolidation_candidates": candidates,
        "resolved_consolidations": resolved,
        "summary": analysis_summary(issues, candidates, resolved, rows),
    }
