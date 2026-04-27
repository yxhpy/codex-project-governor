#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

STOP = {"the", "and", "for", "with", "this", "that", "from", "into", "add", "fix", "build", "make", "new", "实现", "新增", "修复"}
ROUTE_ROLE_WEIGHTS = {
    "micro_patch": {"agent_instructions": 2, "test": 1, "design": 3, "ui_or_component": 3},
    "standard_feature": {"agent_instructions": 4, "conventions": 4, "test": 5, "code": 3, "api": 3},
    "ui_change": {"design": 5, "ui_or_component": 5, "conventions": 3, "test": 3},
    "risky_feature": {"agent_instructions": 5, "decision": 5, "quality": 4, "test": 5, "auth": 5, "payment": 5, "security": 5, "data_model": 5},
    "upgrade_or_migration": {"decision": 4, "quality": 4, "test": 4, "data_model": 4, "doc": 3},
    "research": {"doc": 4, "decision": 4, "memory": 4, "conventions": 3},
}


def terms(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9_\-]{3,}|[\u4e00-\u9fff]{2,}", text.lower()) if token not in STOP}


def load_index(project: Path) -> dict[str, Any]:
    path = project / ".project-governor" / "context" / "CONTEXT_INDEX.json"
    if not path.exists():
        raise SystemExit(f"Context index not found: {path}. Run build_context_index.py --write first.")
    return json.loads(path.read_text(encoding="utf-8"))


def role_weights(route: str) -> dict[str, int]:
    return ROUTE_ROLE_WEIGHTS.get(route, ROUTE_ROLE_WEIGHTS["standard_feature"])


def stale_reason(project: Path, entry: dict[str, Any]) -> str | None:
    rel = entry.get("path")
    if not rel:
        return "missing_path"
    path = project / rel
    if not path.exists():
        return "file_missing"
    if entry.get("mtime") and int(path.stat().st_mtime) != int(entry.get("mtime")):
        return "mtime_changed"
    return None


def score(entry: dict[str, Any], query_terms: set[str], route: str, changed_files: set[str]) -> tuple[int, list[str]]:
    path_text = entry.get("path", "").lower()
    hay = set(entry.get("tokens", [])) | terms(path_text) | set(entry.get("roles", [])) | {s.lower() for s in entry.get("symbols", [])}
    matched = sorted(query_terms & hay)
    substring_matches = sorted([term for term in query_terms if term in path_text])
    matched = sorted(set(matched) | set(substring_matches))
    score_value = len(matched) * 4 + len(substring_matches) * 2
    roles = set(entry.get("roles", []))
    weights = role_weights(route)
    for role in roles:
        score_value += weights.get(role, 0)
    if entry.get("path") in changed_files:
        score_value += 8
    if entry.get("sensitive"):
        score_value -= 6
    return score_value, matched


def confidence_for(result: list[dict[str, Any]], query_terms: set[str]) -> float:
    if not result:
        return 0.0
    top = result[0]["score"]
    term_coverage = len(set().union(*(set(item.get("matched_terms", [])) for item in result[:5]))) / max(1, len(query_terms))
    return round(max(0.0, min(0.99, (top / 32.0) * 0.60 + term_coverage * 0.39)), 2)


def query(project: Path, request: str, limit: int, route: str = "standard_feature") -> dict[str, Any]:
    index = load_index(project)
    q = terms(request)
    changed_files = set(index.get("git", {}).get("changed_files", []))
    ranked = []
    for entry in index.get("entries", []):
        s, matched = score(entry, q, route, changed_files)
        stale = stale_reason(project, entry)
        if s > 0:
            ranked.append({
                "path": entry["path"],
                "score": s,
                "roles": entry.get("roles", []),
                "matched_terms": matched,
                "summary": entry.get("summary", ""),
                "size": entry.get("size", 0),
                "sensitive": bool(entry.get("sensitive")),
                "stale_reason": stale,
            })
    ranked.sort(key=lambda item: (-item["score"], item["path"]))
    result = ranked[:limit]
    confidence = confidence_for(result, q)
    must_read = ["AGENTS.md"] if (project / "AGENTS.md").exists() else []
    session_brief = ".project-governor/context/SESSION_BRIEF.md"
    if (project / session_brief).exists():
        must_read.append(session_brief)
    for item in result[: min(limit, 12)]:
        if item["path"] not in must_read and not item.get("sensitive"):
            must_read.append(item["path"])
    insufficient_reason = None
    if confidence < 0.35:
        insufficient_reason = "low_confidence_context_match"
    elif not result:
        insufficient_reason = "no_matching_files"
    return {
        "status": "ok",
        "schema": index.get("schema", "project-governor-context-index-v1"),
        "request": request,
        "route": route,
        "confidence": confidence,
        "read_all_initialization_docs": False,
        "recommended_files": result,
        "stale_files": [item["path"] for item in result if item.get("stale_reason")],
        "must_read": must_read,
        "candidate_files": result,
        "insufficient_reason": insufficient_reason,
        "broadened_queries": [request, " ".join(sorted(q))] if insufficient_reason else [],
        "role_weights": role_weights(route),
        "token_policy": {
            "max_files_to_read_first": min(limit, 12),
            "escalate_if_insufficient": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Query Project Governor Harness v6 context index.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--request", required=True)
    parser.add_argument("--route", default="standard_feature")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    print(json.dumps(query(args.project.resolve(), args.request, args.limit, args.route), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
