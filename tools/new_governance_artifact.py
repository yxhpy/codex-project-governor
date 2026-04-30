#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import render_governance_artifact


def ensure_writable(paths: list[Path], force: bool) -> None:
    for path in paths:
        if path.exists() and not force:
            raise SystemExit(f"Refusing to overwrite existing generated artifact file without --force: {path}")


def write_json(path: Path, data: dict[str, Any], force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"Refusing to overwrite existing slot file without --force: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"Refusing to overwrite existing artifact without --force: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def iteration_plan_slots(args: argparse.Namespace) -> dict[str, Any]:
    if not args.user_request:
        raise SystemExit("iteration_plan_v1 requires --user-request.")
    title = args.title or "Iteration Plan"
    return {
        "template_id": "iteration_plan_v1",
        "task_id": args.task_id or args.output_dir.name,
        "title": title,
        "revision": 1,
        "user_request": args.user_request,
        "existing_behavior": [],
        "reuse_patterns": [],
        "expected_changes": [],
        "files_not_to_change": [],
        "new_files": [],
        "dependencies": "No new dependencies expected unless explicitly approved.",
        "tests": [],
        "risks": [],
        "rollback": "Revert the task-specific changes.",
    }


def new_slots(template_id: str, args: argparse.Namespace) -> dict[str, Any]:
    if template_id == "iteration_plan_v1":
        return iteration_plan_slots(args)
    raise SystemExit(f"Unsupported artifact template: {template_id}")


def registry_entry(template_id: str) -> dict[str, Any]:
    templates = render_governance_artifact.load_registry()
    entry = templates.get(template_id)
    if not isinstance(entry, dict):
        raise SystemExit(f"Unknown artifact template: {template_id}")
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Project Governor generated-artifact slot file.")
    parser.add_argument("--template", default="iteration_plan_v1", help="Artifact template id.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory that will receive the slot file.")
    parser.add_argument("--task-id", default="", help="Task id recorded in the slot file.")
    parser.add_argument("--title", default="", help="Optional rendered artifact title.")
    parser.add_argument("--user-request", default="", help="User request recorded in the slot file.")
    parser.add_argument("--render", action="store_true", help="Render the Markdown artifact after writing slots.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated artifact files.")
    args = parser.parse_args()

    template_id = str(args.template)
    entry = registry_entry(template_id)
    slots = new_slots(template_id, args)
    slot_output = args.output_dir / str(entry.get("source_slot_filename") or f"{template_id}.slots.json")
    render_output: Path | None = None
    if args.render:
        render_output = args.output_dir / str(entry.get("output_filename") or f"{template_id}.md")
    ensure_writable([path for path in [slot_output, render_output] if path], args.force)
    write_json(slot_output, slots, args.force)

    if render_output:
        rendered = render_governance_artifact.render(slots, template_id, slot_output.name)
        write_text(render_output, rendered, args.force)

    print(json.dumps({
        "status": "created",
        "schema": "project-governor-artifact-create-result-v1",
        "template_id": template_id,
        "slot_output": str(slot_output),
        "render_output": str(render_output) if render_output else None,
        "revision": int(slots.get("revision") or 1),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
