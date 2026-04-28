#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

STOP = {"the", "and", "for", "with", "this", "that", "from", "into", "add", "fix", "build", "make", "new", "实现", "新增", "修复"}
MEMORY_SEARCH_ROLES = {
    "agent_instructions",
    "conventions",
    "decision",
    "design",
    "governance_history",
    "memory",
    "quality",
    "task_history",
}
ROUTE_ROLE_WEIGHTS = {
    "micro_patch": {"agent_instructions": 2, "test": 1, "design": 3, "ui_or_component": 3},
    "standard_feature": {"agent_instructions": 4, "conventions": 4, "test": 5, "code": 3, "api": 3},
    "ui_change": {"design": 5, "ui_or_component": 5, "conventions": 3, "test": 3},
    "risky_feature": {"agent_instructions": 5, "decision": 5, "quality": 4, "test": 5, "auth": 5, "payment": 5, "security": 5, "data_model": 5},
    "upgrade_or_migration": {"decision": 4, "quality": 4, "test": 4, "data_model": 4, "doc": 3},
    "research": {"doc": 4, "decision": 4, "memory": 4, "task_history": 4, "governance_history": 4, "conventions": 3},
    "memory_search": {"memory": 6, "decision": 5, "task_history": 5, "governance_history": 4, "agent_instructions": 3, "quality": 3, "conventions": 3, "design": 2},
}


def terms(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9_\-]{3,}|[\u4e00-\u9fff]{2,}", text.lower()) if token not in STOP}


def build_index(project: Path) -> None:
    script = Path(__file__).with_name("build_context_index.py")
    proc = subprocess.run(
        [sys.executable, str(script), "--project", str(project), "--write"],
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise SystemExit(f"Failed to build context index for {project}: {detail}")


def load_index(project: Path, auto_build: bool = False) -> tuple[dict[str, Any], bool]:
    path = project / ".project-governor" / "context" / "CONTEXT_INDEX.json"
    auto_built = False
    if not path.exists():
        if not auto_build:
            raise SystemExit(f"Context index not found: {path}. Run build_context_index.py --write first.")
        build_index(project)
        auto_built = True
    if not path.exists():
        raise SystemExit(f"Context index build did not create expected file: {path}")
    return json.loads(path.read_text(encoding="utf-8")), auto_built


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


def query(
    project: Path,
    request: str,
    limit: int,
    route: str = "standard_feature",
    memory_search: bool = False,
    auto_build: bool = False,
    include_sensitive: bool = False,
) -> dict[str, Any]:
    index, auto_built = load_index(project, auto_build)
    q = terms(request)
    changed_files = set(index.get("git", {}).get("changed_files", []))
    ranked = []
    for entry in index.get("entries", []):
        roles = set(entry.get("roles", []))
        if memory_search and not (roles & MEMORY_SEARCH_ROLES):
            continue
        if memory_search and entry.get("sensitive") and not include_sensitive:
            continue
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
        insufficient_reason = "low_confidence_memory_match" if memory_search else "low_confidence_context_match"
    elif not result:
        insufficient_reason = "no_matching_memory_files" if memory_search else "no_matching_files"
    return {
        "status": "ok",
        "schema": index.get("schema", "project-governor-context-index-v1"),
        "request": request,
        "route": route,
        "search_mode": "governance_memory" if memory_search else "context",
        "searched_roles": sorted(MEMORY_SEARCH_ROLES) if memory_search else [],
        "auto_built": auto_built,
        "raw_chat_history_search": False,
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


def format_text(data: dict[str, Any]) -> str:
    lines = [
        f"status: {data['status']}",
        f"mode: {data.get('search_mode', 'context')}",
        f"confidence: {data.get('confidence', 0)}",
    ]
    if data.get("insufficient_reason"):
        lines.append(f"insufficient_reason: {data['insufficient_reason']}")
    for item in data.get("recommended_files", []):
        roles = ",".join(item.get("roles", []))
        lines.append(f"- {item['path']} score={item['score']} roles={roles}")
        summary = item.get("summary")
        if summary:
            lines.append(f"  {summary}")
        if item.get("stale_reason"):
            lines.append(f"  stale_reason={item['stale_reason']}")
    if not data.get("recommended_files"):
        lines.append("- no matching files")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Query Project Governor Harness v6 context index.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--request", required=True)
    parser.add_argument("--route", default="standard_feature")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--memory-search", action="store_true", help="Search governance memory/history surfaces instead of general project context.")
    parser.add_argument("--auto-build", action="store_true", help="Build the context index first when it is missing.")
    parser.add_argument("--include-sensitive", action="store_true", help="Allow sensitive indexed files in memory-search results.")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()
    route = "memory_search" if args.memory_search and args.route == "standard_feature" else args.route
    data = query(
        args.project.resolve(),
        args.request,
        args.limit,
        route,
        memory_search=args.memory_search,
        auto_build=args.auto_build,
        include_sensitive=args.include_sensitive,
    )
    if args.format == "text":
        print(format_text(data), end="")
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
