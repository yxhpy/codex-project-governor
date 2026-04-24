#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Iterable

IGNORE_PARTS = {".git", "node_modules", ".venv", "venv", "dist", "build", "coverage", ".next", ".turbo", "__pycache__"}
IGNORE_PREFIXES = (".project-governor/context/", ".project-governor/trash/")
TEXT_EXTS = {".md", ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".toml", ".yaml", ".yml", ".css", ".scss", ".html", ".go", ".rs"}
IMPORTANT_FILES = {"AGENTS.md", "DESIGN.md", "package.json", "pyproject.toml", "pnpm-lock.yaml", "README.md", "README.zh-CN.md"}


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        rel_text = rel.as_posix()
        parts = set(rel.parts)
        if any(part in IGNORE_PARTS for part in parts) or rel_text.startswith(IGNORE_PREFIXES):
            continue
        if path.name in IMPORTANT_FILES or path.suffix.lower() in TEXT_EXTS:
            yield path


def read_text(path: Path, limit: int = 12000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def sha(path: Path) -> str:
    h = hashlib.sha256()
    try:
        h.update(path.read_bytes())
    except Exception:
        return ""
    return h.hexdigest()


def role_for(rel: str, text: str) -> list[str]:
    low = rel.lower()
    roles = []
    if rel == "AGENTS.md" or "agents.md" in low:
        roles.append("agent_instructions")
    if "docs/memory" in low:
        roles.append("memory")
    if "docs/decisions" in low or "adr" in low or "pdr" in low:
        roles.append("decision")
    if "docs/conventions" in low or "pattern" in low or "component_registry" in low:
        roles.append("conventions")
    if "docs/quality" in low or "quality" in low or "gate" in low:
        roles.append("quality")
    if "test" in low or "spec" in low:
        roles.append("test")
    if "component" in low or rel.endswith((".tsx", ".jsx")):
        roles.append("ui_or_component")
    if "api" in low or "route" in low or "controller" in low:
        roles.append("api")
    if "schema" in low or "model" in low or "migration" in low:
        roles.append("data_model")
    if rel == "DESIGN.md" or "design" in low:
        roles.append("design")
    if not roles and rel.endswith(".md"):
        roles.append("doc")
    if not roles:
        roles.append("code")
    return sorted(set(roles))


def tokens(text: str) -> list[str]:
    raw = re.findall(r"[a-zA-Z0-9_\-]{3,}|[\u4e00-\u9fff]{2,}", text.lower())
    stop = {"the", "and", "for", "with", "this", "that", "from", "into", "return", "export", "import"}
    seen = []
    for t in raw:
        if t not in stop and t not in seen:
            seen.append(t)
        if len(seen) >= 60:
            break
    return seen


def build(project: Path) -> dict:
    entries = []
    for path in iter_files(project):
        rel = path.relative_to(project).as_posix()
        text = read_text(path)
        entries.append({
            "path": rel,
            "size": path.stat().st_size,
            "sha256": sha(path),
            "roles": role_for(rel, text),
            "tokens": tokens(rel + "\n" + text),
            "summary": " ".join(text.strip().split()[:35]),
        })
    entries.sort(key=lambda item: ("agent_instructions" not in item["roles"], item["path"]))
    return {
        "schema": "project-governor-context-index-v1",
        "project": str(project),
        "entry_count": len(entries),
        "entries": entries,
    }


def session_brief(index: dict) -> str:
    entries = index["entries"]
    core = [e for e in entries if any(r in e["roles"] for r in ["agent_instructions", "conventions", "quality", "memory", "decision", "design"])]
    lines = [
        "# Project Governor Session Brief",
        "",
        "Use this brief before reading large project docs. Query CONTEXT_INDEX.json for task-specific files.",
        "",
        f"Indexed files: {index['entry_count']}",
        "",
        "## Core references",
        "",
    ]
    for e in core[:25]:
        lines.append(f"- `{e['path']}` — {', '.join(e['roles'])}")
    lines.extend([
        "",
        "## Policy",
        "",
        "- Do not read all initialization documents unless the context query is insufficient.",
        "- Prefer task-specific retrieval from `.project-governor/context/CONTEXT_INDEX.json`.",
        "- Use GPT-5.4-mini for read-only scouting and GPT-5.5 for complex implementation/review when available.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a compact Project Governor context index.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    project = args.project.resolve()
    index = build(project)
    if args.write:
        out = project / ".project-governor" / "context"
        out.mkdir(parents=True, exist_ok=True)
        (out / "CONTEXT_INDEX.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out / "SESSION_BRIEF.md").write_text(session_brief(index), encoding="utf-8")
        (out / "INDEX_REPORT.json").write_text(json.dumps({"status": "written", "entry_count": index["entry_count"]}, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "written", "index": str(out / "CONTEXT_INDEX.json"), "brief": str(out / "SESSION_BRIEF.md"), "entry_count": index["entry_count"]}, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(index, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
