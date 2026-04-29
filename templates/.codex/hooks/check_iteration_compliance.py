#!/usr/bin/env python3
"""Lightweight optional Codex hook.

This hook intentionally avoids blocking normal work unless obvious hazards are
found in staged changes. It is a hint layer, not the source of truth. The real
policy lives in AGENTS.md, docs/conventions, tests, and review.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()


def run_git(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def staged_files() -> list[str]:
    return run_git(["diff", "--name-only", "--cached"]).splitlines()


def package_metadata_changed(changed: list[str]) -> bool:
    package_files = {"package.json", "pnpm-lock.yaml", "package-lock.json", "yarn.lock", "uv.lock", "poetry.lock"}
    return any(Path(path).name in package_files for path in changed)


def app_change_count(changed: list[str]) -> int:
    return len([path for path in changed if path.startswith(("src/", "app/", "packages/", "services/"))])


def governance_warnings(changed: list[str]) -> list[str]:
    warnings: list[str] = []
    if package_metadata_changed(changed):
        warnings.append("Dependency or package metadata changed; ensure a decision note exists if this is a production dependency change.")
    if app_change_count(changed) > 12:
        warnings.append("Large application change detected; verify this is an iteration and not an accidental rewrite.")
    return warnings


def print_warnings(warnings: list[str]) -> None:
    if not warnings:
        return
    print("Project Governor governance hints:")
    for item in warnings:
        print(f"- {item}")


def main() -> int:
    changed = staged_files()
    if not changed:
        return 0
    print_warnings(governance_warnings(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
