#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "coverage", "Library", ".cache"}


def read_text(path: Path, limit: int = 12000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def evidence_for(path: Path) -> list[str]:
    evidence: list[str] = []
    if (path / ".project-governor" / "INSTALL_MANIFEST.json").exists():
        evidence.append(".project-governor/INSTALL_MANIFEST.json")
    if (path / "AGENTS.md").exists() and "Project Governor" in read_text(path / "AGENTS.md"):
        evidence.append("AGENTS.md mentions Project Governor")
    if (path / "docs" / "conventions" / "ITERATION_CONTRACT.md").exists():
        evidence.append("docs/conventions/ITERATION_CONTRACT.md")
    if (path / "docs" / "memory" / "PROJECT_MEMORY.md").exists() and "Project Governor" in read_text(path / "docs" / "memory" / "PROJECT_MEMORY.md"):
        evidence.append("docs/memory/PROJECT_MEMORY.md mentions Project Governor")
    return evidence


def looks_like_plugin_source(path: Path) -> bool:
    manifest = path / ".codex-plugin" / "plugin.json"
    return manifest.exists() and "codex-project-governor" in read_text(manifest)


def child_dirs(path: Path) -> list[Path]:
    try:
        return sorted([child for child in path.iterdir() if child.is_dir()])
    except OSError:
        return []


def skip_child(path: Path) -> bool:
    return path.name in SKIP_DIRS or (path.name.startswith(".") and path.name not in {".project-governor", ".codex"})


def candidate_children(path: Path) -> list[Path]:
    return [child for child in child_dirs(path) if not skip_child(child)]


def iter_candidate_dirs(root: Path, max_depth: int) -> Iterable[Path]:
    root = root.expanduser().resolve()
    if not root.exists():
        return
    stack: list[tuple[Path, int]] = [(root, 0)]
    while stack:
        current, depth = stack.pop()
        yield current
        if depth >= max_depth:
            continue
        for child in reversed(candidate_children(current)):
            stack.append((child, depth + 1))


def discover(roots: list[Path], max_depth: int) -> dict:
    projects: list[dict] = []
    seen: set[str] = set()
    for root in roots:
        for path in iter_candidate_dirs(root, max_depth):
            resolved = str(path.resolve())
            if resolved in seen:
                continue
            seen.add(resolved)
            evidence = evidence_for(path)
            if evidence:
                projects.append({
                    "path": resolved,
                    "evidence": evidence,
                    "is_plugin_source": looks_like_plugin_source(path),
                    "recommendation": "review_as_plugin_root" if looks_like_plugin_source(path) else "eligible_for_project_refresh",
                })
    return {
        "status": "discovered",
        "project_count": len(projects),
        "projects": projects,
        "user_choices": ["ignore", "all", "selected"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--max-depth", type=int, default=4)
    args = parser.parse_args()
    roots = args.root or [Path.cwd(), Path.home()]
    print(json.dumps(discover(roots, args.max_depth), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
