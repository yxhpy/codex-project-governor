#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "templates" / "artifacts" / "ARTIFACT_TEMPLATES.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry() -> dict[str, Any]:
    if not REGISTRY.exists():
        raise SystemExit(f"Artifact template registry not found: {REGISTRY}")
    data = load_json(REGISTRY)
    templates = data.get("templates")
    if not isinstance(templates, dict):
        raise SystemExit("Artifact template registry is missing templates object.")
    return templates


def bullet_for_mapping(item: dict[str, Any]) -> str:
    text = item.get("text") or item.get("path") or item.get("command") or item.get("value") or item.get("summary")
    detail = item.get("reason") or item.get("status") or item.get("notes")
    if text and detail:
        return f"- {text}: {detail}"
    if text:
        return f"- {text}"
    return f"- {json.dumps(item, ensure_ascii=False, sort_keys=True)}"


def bullet_for(item: Any) -> str:
    if isinstance(item, str):
        return f"- {item}"
    if isinstance(item, dict):
        return bullet_for_mapping(item)
    return f"- {item}"


def as_lines(items: list[Any]) -> list[str]:
    return [bullet_for(item) for item in items] or ["- None recorded."]


def str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def slot_list(slots: dict[str, Any], key: str) -> list[Any]:
    value = slots.get(key)
    return list(value) if isinstance(value, list) else []


def slot_string(slots: dict[str, Any], key: str, default: str) -> str:
    value = slots.get(key)
    return str(value) if value not in (None, "") else default


def slot_revision(slots: dict[str, Any]) -> int:
    return int(slots.get("revision", 1))


def table_row(values: list[str]) -> str:
    return "| " + " | ".join(value.replace("\n", " ").strip() for value in values) + " |"


def render_reuse_patterns(items: list[Any]) -> list[str]:
    lines = [
        table_row(["Pattern", "Source file", "How it will be reused"]),
        table_row(["---", "---", "---"]),
    ]
    for item in items:
        if isinstance(item, dict):
            lines.append(table_row([str(item.get("pattern", "")), str(item.get("source", "")), str(item.get("reuse", ""))]))
        else:
            lines.append(table_row([str(item), "", ""]))
    return lines if len(lines) > 2 else [*lines, table_row(["None recorded.", "", ""])]


def render_new_files(items: list[Any]) -> list[str]:
    lines = [
        table_row(["File", "Why existing files cannot cover it"]),
        table_row(["---", "---"]),
    ]
    for item in items:
        if isinstance(item, dict):
            lines.append(table_row([str(item.get("file", "")), str(item.get("why", ""))]))
        else:
            lines.append(table_row([str(item), ""]))
    return lines if len(lines) > 2 else [*lines, table_row(["None expected.", ""])]


def render_dependencies(value: Any) -> list[str]:
    if isinstance(value, list):
        return as_lines(str_list(value))
    return [str(value or "No new dependencies expected unless explicitly approved.")]


def render_revision_history(items: list[Any]) -> list[str]:
    if not items:
        return []
    lines = ["## Revision history", ""]
    for item in items:
        if isinstance(item, dict):
            rev = item.get("revision") or item.get("to_revision") or "?"
            reason = item.get("reason") or "No reason recorded."
            lines.append(f"- r{rev}: {reason}")
        else:
            lines.append(f"- {item}")
    return [*lines, ""]


def render_iteration_plan(slots: dict[str, Any], source_name: str) -> str:
    template_id = slot_string(slots, "template_id", "iteration_plan_v1")
    revision = slot_revision(slots)
    title = slot_string(slots, "title", "Iteration Plan")
    lines = [
        f"<!-- generated_from: {template_id}; source: {source_name}; revision: {revision} -->",
        f"# {title}",
        "",
        "## User request",
        "",
        slot_string(slots, "user_request", "None recorded."),
        "",
        "## Existing behavior",
        "",
        *as_lines(slot_list(slots, "existing_behavior")),
        "",
        "## Existing patterns to reuse",
        "",
        *render_reuse_patterns(slot_list(slots, "reuse_patterns")),
        "",
        "## Files expected to change",
        "",
        *as_lines(slot_list(slots, "expected_changes")),
        "",
        "## Files not to change",
        "",
        *as_lines(slot_list(slots, "files_not_to_change")),
        "",
        "## New files",
        "",
        *render_new_files(slot_list(slots, "new_files")),
        "",
        "## Dependencies",
        "",
        *render_dependencies(slots.get("dependencies")),
        "",
        "## Tests",
        "",
        *as_lines(slot_list(slots, "tests")),
        "",
        "## Risks",
        "",
        *as_lines(slot_list(slots, "risks")),
        "",
        "## Rollback",
        "",
        slot_string(slots, "rollback", "Revert the task-specific changes."),
        "",
    ]
    lines.extend(render_revision_history(slot_list(slots, "revision_history")))
    return "\n".join(lines)


def validate_slots(slots: dict[str, Any], template_id: str) -> None:
    if slots.get("template_id") and slots["template_id"] != template_id:
        raise SystemExit(f"Slot template_id {slots['template_id']!r} does not match requested template {template_id!r}.")
    if template_id == "iteration_plan_v1" and not slots.get("user_request"):
        raise SystemExit("iteration_plan_v1 requires user_request.")


def render(slots: dict[str, Any], template_id: str, source_name: str) -> str:
    validate_slots(slots, template_id)
    if template_id == "iteration_plan_v1":
        return render_iteration_plan(slots, source_name)
    raise SystemExit(f"Unsupported artifact template: {template_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Project Governor governance artifacts from variable slots.")
    parser.add_argument("--template", default=None, help="Artifact template id. Defaults to input template_id.")
    parser.add_argument("--input", type=Path, required=True, help="Slot JSON input.")
    parser.add_argument("--output", type=Path, help="Markdown output path.")
    args = parser.parse_args()

    slots = load_json(args.input)
    if not isinstance(slots, dict):
        raise SystemExit("Slot input must be a JSON object.")
    template_id = args.template or str(slots.get("template_id") or "")
    if not template_id:
        raise SystemExit("Provide --template or template_id in the slot input.")
    templates = load_registry()
    if template_id not in templates:
        raise SystemExit(f"Unknown artifact template: {template_id}")
    rendered = render(slots, template_id, args.input.name)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(json.dumps({
        "status": "rendered",
        "schema": "project-governor-artifact-render-result-v1",
        "template_id": template_id,
        "input": str(args.input),
        "output": str(args.output) if args.output else None,
        "revision": int(slots.get("revision") or 1),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
