#!/usr/bin/env python3
"""Lightweight repository convention detector.

This is intentionally conservative. It returns evidence for package manager,
framework hints, language hints, test files, and likely source roots.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

LOCKFILES = {
    "pnpm-lock.yaml": "pnpm",
    "package-lock.json": "npm",
    "yarn.lock": "yarn",
    "bun.lockb": "bun",
    "poetry.lock": "poetry",
    "uv.lock": "uv",
    "Cargo.lock": "cargo",
    "go.sum": "go",
}

SRC_DIRS = ["src", "app", "apps", "packages", "services", "lib", "components"]
TEST_PATTERNS = (".test.", ".spec.", "__tests__")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def detect(root: Path) -> dict[str, Any]:
    files = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]
    package_manager = []
    for lockfile, name in LOCKFILES.items():
        if (root / lockfile).exists():
            package_manager.append({"name": name, "evidence": lockfile})

    languages = set()
    for p in files:
        if p.suffix in {".ts", ".tsx"}:
            languages.add("TypeScript")
        elif p.suffix in {".js", ".jsx"}:
            languages.add("JavaScript")
        elif p.suffix == ".py":
            languages.add("Python")
        elif p.suffix == ".rs":
            languages.add("Rust")
        elif p.suffix == ".go":
            languages.add("Go")

    package_json = root / "package.json"
    frameworks = []
    if package_json.exists():
        try:
            pkg = json.loads(package_json.read_text(encoding="utf-8"))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            for key in ["react", "next", "vue", "svelte", "express", "fastify", "vite", "vitest", "jest"]:
                if key in deps:
                    frameworks.append({"name": key, "evidence": "package.json"})
        except json.JSONDecodeError:
            frameworks.append({"name": "package.json-unreadable", "evidence": "package.json"})

    source_roots = [d for d in SRC_DIRS if (root / d).exists()]
    test_files = [rel(p, root) for p in files if any(pattern in p.as_posix() for pattern in TEST_PATTERNS)]

    return {
        "package_manager": package_manager,
        "languages": sorted(languages),
        "frameworks": frameworks,
        "source_roots": source_roots,
        "test_files": sorted(test_files)[:50],
        "file_count": len(files),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect basic repository conventions.")
    parser.add_argument("repo", type=Path, nargs="?", default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(detect(args.repo.resolve()), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
