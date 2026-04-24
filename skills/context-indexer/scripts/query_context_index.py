#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

STOP = {"the", "and", "for", "with", "this", "that", "from", "into", "add", "fix", "build", "make", "新增", "修复", "实现"}


def terms(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z0-9_\-]{3,}|[\u4e00-\u9fff]{2,}", text.lower()) if t not in STOP}


def load_index(project: Path) -> dict:
    path = project / ".project-governor" / "context" / "CONTEXT_INDEX.json"
    if not path.exists():
        raise SystemExit(f"Context index not found: {path}. Run build_context_index.py --write first.")
    return json.loads(path.read_text(encoding="utf-8"))


def score(entry: dict, query_terms: set[str]) -> tuple[int, list[str]]:
    path_text = entry.get("path", "").lower()
    hay = set(entry.get("tokens", [])) | terms(path_text) | set(entry.get("roles", []))
    matched = sorted(query_terms & hay)
    substring_matches = sorted([term for term in query_terms if term in path_text])
    matched = sorted(set(matched) | set(substring_matches))
    score = len(matched) * 4 + len(substring_matches) * 2
    roles = set(entry.get("roles", []))
    if "agent_instructions" in roles:
        score += 3
    if "test" in roles and {"test", "tests", "测试"} & query_terms:
        score += 4
    if "design" in roles and {"design", "style", "ui", "样式", "设计"} & query_terms:
        score += 4
    if "memory" in roles and {"memory", "remember", "记忆"} & query_terms:
        score += 4
    return score, matched


def query(project: Path, request: str, limit: int) -> dict:
    index = load_index(project)
    q = terms(request)
    ranked = []
    for entry in index.get("entries", []):
        s, matched = score(entry, q)
        if s > 0:
            ranked.append({
                "path": entry["path"],
                "score": s,
                "roles": entry.get("roles", []),
                "matched_terms": matched,
                "summary": entry.get("summary", ""),
                "size": entry.get("size", 0),
            })
    ranked.sort(key=lambda e: (-e["score"], e["path"]))
    result = ranked[:limit]
    return {
        "status": "ok",
        "request": request,
        "read_all_initialization_docs": False,
        "recommended_files": result,
        "token_policy": {
            "max_files_to_read_first": min(limit, 12),
            "escalate_if_insufficient": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Query Project Governor context index.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--request", required=True)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    print(json.dumps(query(args.project.resolve(), args.request, args.limit), indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
