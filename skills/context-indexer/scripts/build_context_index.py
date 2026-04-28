#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

IGNORE_PARTS = {".git", "node_modules", ".venv", "venv", "dist", "build", "coverage", ".next", ".turbo", "__pycache__"}
IGNORE_PREFIXES = (
    ".project-governor/context/",
    ".project-governor/runtime/",
    ".project-governor/evidence/",
    ".project-governor/trash/",
    ".project-governor/backups/",
)
TEXT_EXTS = {".md", ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".toml", ".yaml", ".yml", ".css", ".scss", ".html", ".go", ".rs", ".vue", ".svelte"}
IMPORTANT_FILES = {"AGENTS.md", "DESIGN.md", "package.json", "pyproject.toml", "pnpm-lock.yaml", "package-lock.json", "yarn.lock", "README.md", "README.zh-CN.md"}
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|private[_-]?key)\s*[:=]\s*['\"]?[^'\"\s]{8,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(project: Path, args: list[str]) -> str | None:
    try:
        proc = subprocess.run(["git", *args], cwd=project, text=True, capture_output=True, timeout=5, check=False)
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def git_metadata(project: Path) -> dict[str, object]:
    head = run_git(project, ["rev-parse", "HEAD"])
    changed = run_git(project, ["status", "--porcelain"])
    changed_files: list[str] = []
    if changed:
        for line in changed.splitlines():
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            changed_files.append(path)
    return {"head": head, "dirty": bool(changed), "changed_files": changed_files}


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        rel_text = rel.as_posix()
        if any(part in IGNORE_PARTS for part in rel.parts) or rel_text.startswith(IGNORE_PREFIXES):
            continue
        if path.name in IMPORTANT_FILES or path.suffix.lower() in TEXT_EXTS:
            yield path


def read_text(path: Path, limit: int = 32_000) -> str:
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


def language_for(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".py": "python", ".ts": "typescript", ".tsx": "typescript-react", ".js": "javascript", ".jsx": "javascript-react",
        ".go": "go", ".rs": "rust", ".md": "markdown", ".json": "json", ".yaml": "yaml", ".yml": "yaml",
        ".toml": "toml", ".css": "css", ".scss": "scss", ".html": "html", ".vue": "vue", ".svelte": "svelte",
    }.get(ext, "text")


def contains_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def redact(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    return redacted


def role_for(rel: str, text: str) -> list[str]:
    low = rel.lower()
    sample = text.lower()
    roles: list[str] = []
    if rel == "AGENTS.md" or "agents.md" in low:
        roles.append("agent_instructions")
    if "docs/memory" in low or ".project-governor/state" in low:
        roles.append("memory")
    if low.startswith("tasks/") or ".project-governor/state" in low:
        roles.append("task_history")
    if low.startswith(("docs/upgrades/", "docs/research/", "releases/")):
        roles.append("governance_history")
    if "docs/decisions" in low or "adr" in low or "pdr" in low:
        roles.append("decision")
    if "docs/conventions" in low or "pattern" in low or "component_registry" in low:
        roles.append("conventions")
    if "docs/quality" in low or "quality" in low or "gate" in low:
        roles.append("quality")
    if "test" in low or "spec" in low:
        roles.append("test")
    if "component" in low or rel.endswith((".tsx", ".jsx", ".vue", ".svelte")):
        roles.append("ui_or_component")
    if "api" in low or "route" in low or "controller" in low or "endpoint" in sample:
        roles.append("api")
    if "schema" in low or "model" in low or "migration" in low:
        roles.append("data_model")
    if rel == "DESIGN.md" or "design" in low or "token" in low:
        roles.append("design")
    if any(term in low or term in sample for term in ["auth", "oauth", "session", "permission", "rbac", "login"]):
        roles.append("auth")
    if any(term in low or term in sample for term in ["payment", "billing", "invoice", "refund", "checkout"]):
        roles.append("payment")
    if contains_secret(text) or any(term in sample for term in ["secret", "token", "password", "private key"]):
        roles.append("security")
    if not roles and rel.endswith(".md"):
        roles.append("doc")
    if not roles:
        roles.append("code")
    return sorted(set(roles))


def tokens(text: str) -> list[str]:
    safe = redact(text.lower())
    raw = re.findall(r"[a-zA-Z0-9_\-]{3,}|[\u4e00-\u9fff]{2,}", safe)
    stop = {"the", "and", "for", "with", "this", "that", "from", "into", "return", "export", "import", "const", "function"}
    seen: list[str] = []
    for token in raw:
        if token in stop or token == "redacted_secret":
            continue
        if token not in seen:
            seen.append(token)
        if len(seen) >= 120:
            break
    return seen


def extract_symbols(language: str, text: str) -> list[str]:
    patterns: list[str] = []
    if language == "python":
        patterns = [r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)", r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)"]
    elif language.startswith("typescript") or language.startswith("javascript"):
        patterns = [
            r"\bfunction\s+([A-Za-z_$][A-Za-z0-9_$]*)",
            r"\bclass\s+([A-Za-z_$][A-Za-z0-9_$]*)",
            r"\b(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=",
            r"\binterface\s+([A-Za-z_$][A-Za-z0-9_$]*)",
            r"\btype\s+([A-Za-z_$][A-Za-z0-9_$]*)",
        ]
    found: list[str] = []
    for pattern in patterns:
        flags = re.MULTILINE
        for match in re.findall(pattern, text, flags=flags):
            if match not in found:
                found.append(match)
            if len(found) >= 60:
                return found
    return found


def extract_imports(language: str, text: str) -> list[str]:
    found: list[str] = []
    patterns = []
    if language == "python":
        patterns = [r"^\s*import\s+([A-Za-z0-9_\.]+)", r"^\s*from\s+([A-Za-z0-9_\.]+)\s+import"]
    elif language.startswith("typescript") or language.startswith("javascript"):
        patterns = [r"from\s+['\"]([^'\"]+)['\"]", r"import\(['\"]([^'\"]+)['\"]\)"]
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.MULTILINE):
            if match not in found:
                found.append(match)
            if len(found) >= 80:
                return found
    return found


def extract_headings(text: str) -> list[str]:
    headings = [m.group(1).strip() for m in re.finditer(r"^#{1,4}\s+(.+)$", text, flags=re.MULTILINE)]
    return headings[:40]


def summarize(text: str) -> str:
    safe = redact(text)
    words = " ".join(safe.strip().split()[:45])
    return words


def build(project: Path) -> dict:
    entries = []
    for path in iter_files(project):
        rel = path.relative_to(project).as_posix()
        text = read_text(path)
        language = language_for(path)
        stat = path.stat()
        sensitive = contains_secret(text)
        entries.append({
            "path": rel,
            "size": stat.st_size,
            "mtime": int(stat.st_mtime),
            "sha256": sha(path),
            "language": language,
            "roles": role_for(rel, text),
            "symbols": [] if sensitive else extract_symbols(language, text),
            "imports": [] if sensitive else extract_imports(language, text),
            "headings": extract_headings(redact(text)),
            "tokens": tokens(rel + "\n" + text),
            "summary": summarize(text),
            "sensitive": sensitive,
            "stale_reason": None,
        })
    entries.sort(key=lambda item: ("agent_instructions" not in item["roles"], item["path"]))
    return {
        "schema": "project-governor-context-index-v2",
        "built_at": utc_now(),
        "project": str(project),
        "project_fingerprint": hashlib.sha256("\n".join(e["sha256"] for e in entries).encode()).hexdigest()[:16],
        "git": git_metadata(project),
        "entry_count": len(entries),
        "entries": entries,
    }


def session_brief(index: dict) -> str:
    entries = index["entries"]
    core = [e for e in entries if any(r in e["roles"] for r in ["agent_instructions", "conventions", "quality", "memory", "decision", "task_history", "governance_history", "design"])]
    lines = [
        "# Project Governor Harness v6 Session Brief",
        "",
        "Use this brief before reading large project docs. Query CONTEXT_INDEX.json for task-specific files.",
        "",
        f"Schema: `{index['schema']}`",
        f"Indexed files: {index['entry_count']}",
        f"Git head: `{index.get('git', {}).get('head') or 'unknown'}`",
        f"Dirty working tree: `{index.get('git', {}).get('dirty')}`",
        "",
        "## Core references",
        "",
    ]
    for entry in core[:25]:
        suffix = " sensitive" if entry.get("sensitive") else ""
        lines.append(f"- `{entry['path']}` — {', '.join(entry['roles'])}{suffix}")
    lines.extend([
        "",
        "## Policy",
        "",
        "- Do not read all initialization documents unless the context query is insufficient.",
        "- Prefer task-specific retrieval from `.project-governor/context/CONTEXT_INDEX.json`.",
        "- Start non-trivial work with `.project-governor/state/SESSION.json` and finish with evidence.",
        "- Use fast read-only scouting for retrieval and high-reasoning models for implementation/review when available.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Project Governor Harness v6 context index.")
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
        (out / "INDEX_REPORT.json").write_text(json.dumps({"status": "written", "schema": index["schema"], "entry_count": index["entry_count"], "built_at": index["built_at"]}, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "written", "index": str(out / "CONTEXT_INDEX.json"), "brief": str(out / "SESSION_BRIEF.md"), "entry_count": index["entry_count"], "schema": index["schema"]}, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(index, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
