#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py"}
IGNORED_DIRS = {".git", "node_modules", "dist", "build", ".next", "coverage"}
EXPORT_RE = re.compile(r"(?:export\s+)?(?:function|class|const|interface|type)\s+([A-Z_a-z][A-Z_a-z0-9]*)")


def category(path: Path, symbol: str) -> str:
    lower_path = path.as_posix().lower()
    if "fixture" in lower_path or "mock" in lower_path or "testdata" in lower_path:
        return "test_double"
    if "hook" in lower_path or symbol.startswith("use"):
        return "hook"
    if "service" in lower_path or "client" in lower_path:
        return "service"
    if "schema" in lower_path or "model" in lower_path:
        return "schema"
    if "test" in lower_path or "spec" in lower_path:
        return "test_pattern"
    if "component" in lower_path or path.suffix in {".tsx", ".jsx"} or symbol[:1].isupper():
        return "component"
    return "utility"


def iter_source_files(repo: Path) -> list[Path]:
    return [
        path
        for path in repo.rglob("*")
        if path.is_file() and path.suffix in EXTENSIONS and not any(part in IGNORED_DIRS for part in path.parts)
    ]


def symbols_for(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    symbols = EXPORT_RE.findall(text)
    if symbols:
        return symbols
    return [path.stem] if path.name[0].isalpha() else []


def find(repo: Path, request: str = "") -> dict[str, Any]:
    terms = set(re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", request.lower()))
    candidates: list[dict[str, Any]] = []

    for path in iter_source_files(repo):
        for symbol in symbols_for(path)[:6]:
            haystack = f"{path.as_posix()} {symbol}".lower()
            score = sum(1 for term in terms if term in haystack)
            item_category = category(path, symbol)
            if score or item_category in {"component", "hook", "service", "schema", "test_pattern", "test_double"}:
                candidates.append(
                    {
                        "name": symbol,
                        "category": item_category,
                        "path": path.relative_to(repo).as_posix(),
                        "score": score,
                        "reuse_guidance": f"Reuse existing {item_category} before creating a new parallel implementation.",
                    }
                )

    candidates.sort(key=lambda item: (-item["score"], item["category"], item["path"], item["name"]))
    return {
        "status": "found",
        "required_reuse": [candidate for candidate in candidates if candidate["score"] > 0][:8],
        "reuse_candidates": candidates[:30],
        "forbidden_duplicates": [
            {
                "existing": candidate["name"],
                "path": candidate["path"],
                "message": "Do not create a duplicate without explaining why this cannot be reused.",
            }
            for candidate in candidates[:10]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--request", default="")
    args = parser.parse_args()
    print(json.dumps(find(args.repo.resolve(), args.request), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
