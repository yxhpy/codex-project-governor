#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".md", ".json", ".yml", ".yaml", ".toml", ".go", ".rs", ".vue", ".svelte"}
IGNORED_DIRS = {".git", "node_modules", "dist", "build", ".next", "coverage", "vendor", ".venv", "venv", "__pycache__"}
IGNORED_PREFIXES = (
    ".project-governor/context/",
    ".project-governor/runtime/",
    ".project-governor/evidence/",
    ".project-governor/backups/",
    ".project-governor/trash/",
)
STOP_WORDS = {"the", "and", "for", "with", "add", "new", "fix", "make", "user", "users", "a", "an", "to", "of", "in", "on"}
ROOT = Path(__file__).resolve().parents[3]
QUERY_INDEX = ROOT / "skills" / "context-indexer" / "scripts" / "query_context_index.py"


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower()) if token not in STOP_WORDS]


def ignored(repo: Path, path: Path) -> bool:
    rel = path.relative_to(repo).as_posix()
    return any(part in IGNORED_DIRS for part in path.parts) or rel.startswith(IGNORED_PREFIXES)


def iter_candidate_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file() and path.suffix in EXTENSIONS and not ignored(root, path)]


def score_file(path: Path, terms: list[str]) -> tuple[int, list[str]]:
    relative_path = path.as_posix().lower()
    hits = {term for term in terms if term in relative_path}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()[:20000]
    except OSError:
        text = ""
    hits |= {term for term in terms if term in text}
    score = len(hits)
    if "test" in relative_path or "spec" in relative_path:
        score += 1
    if any(kind in relative_path for kind in ["component", "service", "api", "route", "hook"]):
        score += 1
    return score, sorted(hits)


def make_item(repo: Path, path: Path, score: int, hits: list[str], source: str = "scan") -> dict[str, Any]:
    return {
        "path": path.relative_to(repo).as_posix(),
        "score": score,
        "matched_terms": hits,
        "source": source,
        "reason": "matches request terms or adjacent project patterns",
    }


def load_index_query() -> Any | None:
    if not QUERY_INDEX.exists():
        return None
    spec = importlib.util.spec_from_file_location("project_governor_query_context_index", QUERY_INDEX)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def from_index(repo: Path, request: str, limit: int, route: str) -> tuple[list[dict[str, Any]], float, dict[str, Any]]:
    if not (repo / ".project-governor" / "context" / "CONTEXT_INDEX.json").exists():
        return [], 0.0, {}
    module = load_index_query()
    if module is None:
        return [], 0.0, {}
    try:
        result = module.query(repo, request, limit, route)
    except Exception:
        return [], 0.0, {}
    items = []
    for row in result.get("recommended_files", []):
        path = repo / row["path"]
        if path.exists() and path.is_file() and not row.get("sensitive"):
            item = make_item(repo, path, int(row.get("score", 1)), list(row.get("matched_terms", [])), source="context-index")
            item["roles"] = row.get("roles", [])
            item["recommended_sections"] = row.get("recommended_sections", [])
            item["doc_status"] = row.get("doc_status", "active")
            items.append(item)
    return items, float(result.get("confidence", 0.0)), {
        "must_read_sections": result.get("must_read_sections", []),
        "recommended_sections": result.get("recommended_sections", []),
        "progressive_read_plan": result.get("progressive_read_plan", []),
        "context_compression": result.get("context_compression", {}),
        "token_policy": result.get("token_policy", {}),
        "avoid_docs": result.get("avoid_docs", []),
    }


def categorize(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    relevant_files: list[dict[str, Any]] = []
    tests: list[dict[str, Any]] = []
    docs: list[dict[str, Any]] = []
    for item in items:
        lower_path = item["path"].lower()
        if "test" in lower_path or "spec" in lower_path:
            tests.append(item)
        elif lower_path.endswith(".md") or "/docs/" in lower_path:
            docs.append(item)
        else:
            relevant_files.append(item)
    return relevant_files[:8], tests[:5], docs[:5], relevant_files[8:12]


def build(repo: Path, request: str, limit: int = 12, route: str = "standard_feature") -> dict[str, Any]:
    terms = tokenize(request)
    indexed, confidence, index_meta = from_index(repo, request, limit, route)
    source = "context-index" if indexed and confidence >= 0.25 else "bounded-scan"
    if indexed and confidence >= 0.25:
        must_read, tests, docs, maybe = categorize(indexed[:limit])
    else:
        ranked: list[tuple[int, Path, list[str]]] = []
        for path in iter_candidate_files(repo):
            score, hits = score_file(path, terms)
            if score > 0:
                ranked.append((score, path, hits))
        ranked.sort(key=lambda item: (-item[0], item[1].as_posix()))
        items = [make_item(repo, path, score, hits, source="bounded-scan") for score, path, hits in ranked[:limit]]
        must_read, tests, docs, maybe = categorize(items)
    return {
        "status": "built",
        "schema": "project-governor-context-pack-v2",
        "source": source,
        "context_index_confidence": confidence,
        "request_terms": terms,
        "must_read": must_read,
        "related_tests": tests,
        "related_docs": docs,
        "maybe_read": maybe,
        "must_read_sections": index_meta.get("must_read_sections", []),
        "progressive_read_plan": index_meta.get("progressive_read_plan", []),
        "compression_policy": index_meta.get("context_compression", {
            "strategy": "bounded_file_scan",
            "use_section_summaries_first": False,
            "full_documents_deferred": True,
        }),
        "token_budget": {
            "max_files_to_read_first": index_meta.get("token_policy", {}).get("max_files_to_read_first", min(limit, 12)),
            "max_sections_to_read_first": index_meta.get("token_policy", {}).get("max_sections_to_read_first", 0),
            "max_total_chars_first": index_meta.get("token_policy", {}).get("max_total_chars_first", 60_000),
            "full_doc_requires_reason": index_meta.get("token_policy", {}).get("full_doc_requires_reason", True),
        },
        "avoid": ["node_modules", "dist", "build", ".git", ".project-governor/context", ".project-governor/evidence"],
        "avoid_docs": index_meta.get("avoid_docs", []),
        "subagents": ["context-scout", "test-scout", "docs-scout"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Harness v6 context pack.")
    parser.add_argument("repo", type=Path)
    parser.add_argument("--request", required=True)
    parser.add_argument("--route", default="standard_feature")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    print(json.dumps(build(args.repo.resolve(), args.request, args.limit, args.route), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
