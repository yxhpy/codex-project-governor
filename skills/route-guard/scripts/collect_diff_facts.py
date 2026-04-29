#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

DEPENDENCY_FILES = {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "pyproject.toml", "requirements.txt", "poetry.lock", "go.mod", "go.sum", "Cargo.toml", "Cargo.lock"}
SCHEMA_HINTS = ("schema", "migration", "migrations", "model", "models", "prisma", "sql", "db")
API_HINTS = ("api", "route", "routes", "controller", "controllers", "openapi", "swagger", "contract")
GLOBAL_STYLE_HINTS = ("globals.css", "global.css", "theme", "tokens", "tailwind.config", "design-token")
SHARED_COMPONENT_HINTS = ("shared", "common", "components/ui", "design-system")


def run_git(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, timeout=10, check=False)


def parse_status(repo: Path) -> dict[str, list[str]]:
    proc = run_git(repo, ["status", "--porcelain"])
    modified: list[str] = []
    added: list[str] = []
    deleted: list[str] = []
    renamed: list[str] = []
    if proc.returncode != 0:
        return {"modified_files": [], "added_files": [], "deleted_files": [], "renamed_files": []}
    for line in proc.stdout.splitlines():
        if not line:
            continue
        code = line[:2]
        path = line[3:].strip()
        if " -> " in path:
            old, new = path.split(" -> ", 1)
            renamed.append(new)
            path = new
        if "D" in code:
            deleted.append(path)
        elif "A" in code or code == "??":
            added.append(path)
        else:
            modified.append(path)
    return {"modified_files": modified, "added_files": added, "deleted_files": deleted, "renamed_files": renamed}


def changed_lines(repo: Path, path: str) -> str:
    proc = run_git(repo, ["diff", "--", path])
    return proc.stdout if proc.returncode == 0 else ""


def has_weakened_assertions(diff_text: str) -> bool:
    removed_assert = bool(re.search(r"^-.*\b(assert|expect|should|toEqual|toBe|pytest|unittest)\b", diff_text, flags=re.MULTILINE))
    added_skip = bool(re.search(r"^\+.*\b(skip|only|xfail|todo)\b", diff_text, flags=re.MULTILINE))
    return removed_assert or added_skip


def paths_with_hints(paths: list[str], hints: tuple[str, ...]) -> list[str]:
    return [p for p in paths if any(hint in p.lower() for hint in hints)]


def dependency_paths(paths: list[str]) -> list[str]:
    return [p for p in paths if Path(p).name in DEPENDENCY_FILES]


def test_paths(paths: list[str]) -> list[str]:
    return [p for p in paths if "test" in p.lower() or "spec" in p.lower()]


def changed_path_groups(status: dict[str, list[str]]) -> dict[str, Any]:
    all_paths = status["modified_files"] + status["added_files"] + status["deleted_files"] + status["renamed_files"]
    return {
        "all_paths": all_paths,
        "dependencies": dependency_paths(all_paths),
        "api_files": paths_with_hints(all_paths, API_HINTS),
        "schema_files": paths_with_hints(all_paths, SCHEMA_HINTS),
        "global_style_files": paths_with_hints(all_paths, GLOBAL_STYLE_HINTS),
        "shared_components": paths_with_hints(all_paths, SHARED_COMPONENT_HINTS),
        "test_files": test_paths(all_paths),
    }


def test_change_flags(repo: Path, status: dict[str, list[str]], test_files: list[str]) -> dict[str, bool]:
    tests_deleted = any(p in status["deleted_files"] for p in test_files)
    assertions_weakened = any(has_weakened_assertions(changed_lines(repo, p)) for p in test_files if p not in status["deleted_files"])
    return {
        "tests_deleted": tests_deleted,
        "assertions_weakened": assertions_weakened,
        "tests_skipped": assertions_weakened,
    }


def collect(repo: Path) -> dict[str, Any]:
    status = parse_status(repo)
    groups = changed_path_groups(status)
    test_flags = test_change_flags(repo, status, groups["test_files"])
    all_paths = groups["all_paths"]
    rewrite_detected = len(all_paths) >= 20 or len(status["deleted_files"]) >= 5
    return {
        "status": "collected",
        "repo": str(repo),
        "modified_files": status["modified_files"],
        "added_files": status["added_files"],
        "deleted_files": status["deleted_files"],
        "renamed_files": status["renamed_files"],
        "dependencies_added": bool(groups["dependencies"]),
        "dependency_files_changed": groups["dependencies"],
        "api_contract_changed": bool(groups["api_files"]),
        "api_files_changed": groups["api_files"],
        "schema_changed": bool(groups["schema_files"]),
        "schema_files_changed": groups["schema_files"],
        "global_style_changed": bool(groups["global_style_files"]),
        "global_style_files_changed": groups["global_style_files"],
        "shared_component_changed": bool(groups["shared_components"]),
        "shared_components_changed": groups["shared_components"],
        "new_components_added": any("component" in p.lower() for p in status["added_files"]),
        "rewrite_detected": rewrite_detected,
        "tests_deleted": test_flags["tests_deleted"],
        "assertions_weakened": test_flags["assertions_weakened"],
        "tests_skipped": test_flags["tests_skipped"],
        "test_files_changed": groups["test_files"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect machine-derived git diff facts for Project Governor route guard.")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(collect(args.repo.resolve()), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
