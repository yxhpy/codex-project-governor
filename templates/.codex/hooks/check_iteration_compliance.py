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


def main() -> int:
    changed = run_git(["diff", "--name-only", "--cached"]).splitlines()
    if not changed:
        return 0

    warnings: list[str] = []
    package_files = {"package.json", "pnpm-lock.yaml", "package-lock.json", "yarn.lock", "uv.lock", "poetry.lock"}
    if any(Path(p).name in package_files for p in changed):
        warnings.append("Dependency or package metadata changed; ensure a decision note exists if this is a production dependency change.")

    if len([p for p in changed if p.startswith(("src/", "app/", "packages/", "services/"))]) > 12:
        warnings.append("Large application change detected; verify this is an iteration and not an accidental rewrite.")

    if warnings:
        print("Project Governor governance hints:")
        for item in warnings:
            print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
