#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".md", ".json", ".yml", ".yaml", ".toml", ".go", ".rs"}
IGNORED_DIRS = {".git", "node_modules", "dist", "build", ".next", "coverage", "vendor"}
STOP_WORDS = {"the", "and", "for", "with", "add", "new", "fix", "make", "user", "users", "a", "an", "to", "of", "in", "on"}


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower()) if token not in STOP_WORDS]


def iter_candidate_files(root: Path) -> list[Path]:
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix in EXTENSIONS and not any(part in IGNORED_DIRS for part in path.parts)
    ]


def score_file(path: Path, terms: list[str]) -> tuple[int, list[str]]:
    relative_path = path.as_posix().lower()
    hits = {term for term in terms if term in relative_path}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        text = ""

    hits |= {term for term in terms if term in text}
    score = len(hits)
    if "test" in relative_path or "spec" in relative_path:
        score += 1
    if any(kind in relative_path for kind in ["component", "service", "api", "route", "hook"]):
        score += 1
    return score, sorted(hits)


def make_item(repo: Path, path: Path, score: int, hits: list[str]) -> dict[str, Any]:
    return {
        "path": path.relative_to(repo).as_posix(),
        "score": score,
        "matched_terms": hits,
        "reason": "matches request terms or adjacent project patterns",
    }


def build(repo: Path, request: str, limit: int = 12) -> dict[str, Any]:
    terms = tokenize(request)
    ranked: list[tuple[int, Path, list[str]]] = []
    for path in iter_candidate_files(repo):
        score, hits = score_file(path, terms)
        if score > 0:
            ranked.append((score, path, hits))

    ranked.sort(key=lambda item: (-item[0], item[1].as_posix()))
    relevant_files: list[dict[str, Any]] = []
    tests: list[dict[str, Any]] = []
    docs: list[dict[str, Any]] = []

    for score, path, hits in ranked[:limit]:
        item = make_item(repo, path, score, hits)
        lower_path = item["path"].lower()
        if "test" in lower_path or "spec" in lower_path:
            tests.append(item)
        elif lower_path.endswith(".md") or "/docs/" in lower_path:
            docs.append(item)
        else:
            relevant_files.append(item)

    return {
        "status": "built",
        "request_terms": terms,
        "must_read": relevant_files[:8],
        "related_tests": tests[:5],
        "related_docs": docs[:5],
        "maybe_read": relevant_files[8:12],
        "avoid": ["node_modules", "dist", "build", ".git"],
        "subagents": ["context-scout", "test-scout", "docs-scout"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--request", required=True)
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    print(json.dumps(build(args.repo.resolve(), args.request, args.limit), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
