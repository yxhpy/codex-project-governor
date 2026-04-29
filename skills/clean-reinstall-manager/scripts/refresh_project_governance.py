#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

PROJECT_TEMPLATE_ALLOW_PREFIXES = (
    "AGENTS.md",
    "docs/",
    "tasks/_template/",
    ".project-governor/",
    ".codex/rules/",
    ".codex/hooks/",
)
PROJECT_TEMPLATE_ALLOW_FILES = {".codex/hooks.json"}
PLUGIN_NOISE_PREFIXES = (
    ".codex/agents/",
    ".codex/prompts/",
    ".codex-plugin/",
    "skills/",
    "templates/",
    "managed-assets/",
    "releases/",
)
PLUGIN_NOISE_FILES = {".codex/config.toml"}
NEVER_OVERWRITE_PREFIXES = ("docs/memory/", "docs/decisions/")


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def is_project(path: Path) -> bool:
    return any([
        (path / ".project-governor" / "INSTALL_MANIFEST.json").exists(),
        (path / "AGENTS.md").exists() and "Project Governor" in read(path / "AGENTS.md"),
        (path / "docs" / "conventions" / "ITERATION_CONTRACT.md").exists(),
    ])


def same_path(left: Path, right: Path) -> bool:
    return left.resolve() == right.resolve()


def allowed_template(rel: str) -> bool:
    return rel in PROJECT_TEMPLATE_ALLOW_FILES or any(rel == prefix.rstrip("/") or rel.startswith(prefix) for prefix in PROJECT_TEMPLATE_ALLOW_PREFIXES)


def iter_templates(plugin_root: Path) -> Iterable[tuple[str, Path]]:
    templates = plugin_root / "templates"
    if not templates.exists():
        return
    for path in sorted(templates.rglob("*")):
        if path.is_file():
            rel = path.relative_to(templates).as_posix()
            if allowed_template(rel):
                yield rel, path


def section_titles(text: str) -> set[str]:
    return {line.strip() for line in text.splitlines() if line.startswith("#")}


def merge_markdown(local: str, template: str) -> tuple[str, list[str]]:
    local_titles = section_titles(local)
    additions: list[str] = []
    current: list[str] = []
    capture = False
    for line in template.splitlines():
        if line.startswith("#"):
            if current and capture:
                additions.append("\n".join(current).rstrip())
            current = [line]
            capture = line.strip() not in local_titles
        else:
            current.append(line)
    if current and capture:
        additions.append("\n".join(current).rstrip())
    if not additions:
        return local, []
    merged = local.rstrip() + "\n\n<!-- Project Governor refresh: appended missing template sections -->\n\n" + "\n\n".join(additions) + "\n"
    return merged, additions


def noise_paths(project: Path) -> list[Path]:
    paths: list[Path] = []
    for prefix in PLUGIN_NOISE_PREFIXES:
        target = project / prefix.rstrip("/")
        if target.exists():
            if target.is_dir():
                paths.extend([p for p in target.rglob("*") if p.is_file()])
            else:
                paths.append(target)
    for rel in PLUGIN_NOISE_FILES:
        target = project / rel
        if target.exists():
            paths.append(target)
    return sorted(set(paths))


def guard_response(project: Path, plugin_root: Path, force: bool) -> dict | None:
    if same_path(project, plugin_root) and not force:
        return {
            "status": "plugin_root_stop",
            "project": str(project),
            "plugin_root": str(plugin_root),
            "message": "Project path is the Project Governor plugin root. No project refresh or quarantine operations were planned.",
        }
    if not is_project(project) and not force:
        return {
            "status": "not_project_stop",
            "project": str(project),
            "message": "Current directory is not a Project Governor project. Discover projects first.",
        }
    return None


def add_missing_operation(rel: str, dest: Path, template_text: str, apply: bool) -> dict:
    operation = {"op": "add_missing", "path": rel, "status": "planned"}
    if apply:
        write(dest, template_text)
        operation["status"] = "applied"
    return operation


def markdown_operation(rel: str, dest: Path, template_text: str, apply: bool, trash_root: Path, project: Path) -> dict:
    local_text = read(dest)
    merged, additions = merge_markdown(local_text, template_text)
    if not additions:
        return {"op": "already_current_or_custom", "path": rel, "status": "kept"}

    operation = {
        "op": "merge_missing_sections",
        "path": rel,
        "section_count": len(additions),
        "status": "planned",
    }
    if apply:
        backup = trash_root / "pre-merge" / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, backup)
        write(dest, merged)
        operation["status"] = "applied"
        operation["backup"] = backup.relative_to(project).as_posix()
    return operation


def template_operation(rel: str, template_path: Path, project: Path, trash_root: Path, apply: bool) -> dict:
    dest = project / rel
    template_text = read(template_path)
    if not dest.exists():
        return add_missing_operation(rel, dest, template_text, apply)
    if rel.startswith(NEVER_OVERWRITE_PREFIXES):
        return {"op": "preserve_append_only", "path": rel, "status": "kept"}
    if dest.is_file() and dest.suffix.lower() in {".md", ""}:
        return markdown_operation(rel, dest, template_text, apply, trash_root, project)
    return {"op": "manual_review", "path": rel, "status": "kept"}


def template_operations(project: Path, plugin_root: Path, trash_root: Path, apply: bool) -> list[dict]:
    return [
        template_operation(rel, template_path, project, trash_root, apply)
        for rel, template_path in iter_templates(plugin_root)
    ]


def noise_operation(project: Path, trash_root: Path, noise: Path, apply: bool, delete_trash: bool) -> dict:
    rel = noise.relative_to(project).as_posix()
    operation = {"op": "quarantine_noise", "path": rel, "status": "planned"}
    if not apply:
        return operation

    if delete_trash:
        if noise.exists():
            noise.unlink()
        operation["status"] = "deleted"
        return operation

    target = trash_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(noise), str(target))
    operation["status"] = "quarantined"
    operation["trash_path"] = target.relative_to(project).as_posix()
    return operation


def noise_operations(project: Path, trash_root: Path, apply: bool, delete_trash: bool) -> list[dict]:
    return [
        noise_operation(project, trash_root, noise, apply, delete_trash)
        for noise in noise_paths(project)
    ]


def operation_summary(operations: list[dict]) -> dict:
    return {
        "add_missing": sum(1 for op in operations if op["op"] == "add_missing"),
        "merge_missing_sections": sum(1 for op in operations if op["op"] == "merge_missing_sections"),
        "quarantine_noise": sum(1 for op in operations if op["op"] == "quarantine_noise"),
        "manual_review": sum(1 for op in operations if op["op"] == "manual_review"),
    }


def refresh(project: Path, plugin_root: Path, apply: bool = False, trash_name: str | None = None, delete_trash: bool = False, force: bool = False) -> dict:
    project = project.resolve()
    plugin_root = plugin_root.resolve()
    blocked = guard_response(project, plugin_root, force)
    if blocked:
        return blocked

    timestamp = trash_name or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    trash_root = project / ".project-governor" / "trash" / timestamp
    operations = template_operations(project, plugin_root, trash_root, apply)
    operations.extend(noise_operations(project, trash_root, apply, delete_trash))

    return {
        "status": "applied" if apply else "planned",
        "project": str(project),
        "plugin_root": str(plugin_root),
        "trash_root": str(trash_root),
        "summary": operation_summary(operations),
        "operations": operations,
        "delete_trash": delete_trash,
        "notes": [
            "Noise is quarantined by default, not deleted.",
            "Memory and decision files are never overwritten.",
            "Existing markdown receives missing template sections only when section headings are absent.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--plugin-root", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--delete-trash", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    result = refresh(args.project, args.plugin_root, args.apply, delete_trash=args.delete_trash, force=args.force)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] in {"planned", "applied", "plugin_root_stop"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
