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


def repo_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts]


def detect_package_managers(root: Path) -> list[dict[str, str]]:
    package_manager: list[dict[str, str]] = []
    for lockfile, name in LOCKFILES.items():
        if (root / lockfile).exists():
            package_manager.append({"name": name, "evidence": lockfile})
    return package_manager


def language_for(path: Path) -> str | None:
    if path.suffix in {".ts", ".tsx"}:
        return "TypeScript"
    if path.suffix in {".js", ".jsx"}:
        return "JavaScript"
    if path.suffix == ".py":
        return "Python"
    if path.suffix == ".rs":
        return "Rust"
    if path.suffix == ".go":
        return "Go"
    return None


def detect_languages(files: list[Path]) -> list[str]:
    return sorted({language for path in files if (language := language_for(path))})


def package_json_dependencies(package_json: Path) -> dict[str, Any]:
    pkg = json.loads(package_json.read_text(encoding="utf-8"))
    return {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}


def detect_frameworks(root: Path) -> list[dict[str, str]]:
    package_json = root / "package.json"
    if not package_json.exists():
        return []
    try:
        deps = package_json_dependencies(package_json)
    except json.JSONDecodeError:
        return [{"name": "package.json-unreadable", "evidence": "package.json"}]
    return [
        {"name": key, "evidence": "package.json"}
        for key in ["react", "next", "vue", "svelte", "express", "fastify", "vite", "vitest", "jest"]
        if key in deps
    ]


def detect_source_roots(root: Path) -> list[str]:
    return [dirname for dirname in SRC_DIRS if (root / dirname).exists()]


def detect_test_files(files: list[Path], root: Path) -> list[str]:
    return sorted(rel(path, root) for path in files if any(pattern in path.as_posix() for pattern in TEST_PATTERNS))[:50]


def detect(root: Path) -> dict[str, Any]:
    files = repo_files(root)

    return {
        "package_manager": detect_package_managers(root),
        "languages": detect_languages(files),
        "frameworks": detect_frameworks(root),
        "source_roots": detect_source_roots(root),
        "test_files": detect_test_files(files, root),
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
