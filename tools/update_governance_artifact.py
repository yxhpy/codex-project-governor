#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import render_governance_artifact


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def pointer_parts(path: str) -> list[str]:
    if not path.startswith("/"):
        raise SystemExit(f"Patch path must be an absolute JSON pointer-like path: {path}")
    return [part.replace("~1", "/").replace("~0", "~") for part in path.split("/")[1:] if part]


def get_parent(data: dict[str, Any], path: str) -> tuple[Any, str]:
    parts = pointer_parts(path)
    if not parts:
        raise SystemExit("Patch path cannot target the document root.")
    current: Any = data
    for part in parts[:-1]:
        if isinstance(current, dict):
            current = current.setdefault(part, {})
        elif isinstance(current, list):
            current = current[int(part)]
        else:
            raise SystemExit(f"Cannot traverse through non-container at {part!r}.")
    return current, parts[-1]


def get_value(data: dict[str, Any], path: str, default: Any = None) -> Any:
    parts = pointer_parts(path)
    current: Any = data
    for part in parts:
        if isinstance(current, dict):
            if part not in current:
                if default is not None:
                    current[part] = default
                else:
                    raise SystemExit(f"Path does not exist: {path}")
            current = current[part]
        elif isinstance(current, list):
            current = current[int(part)]
        else:
            raise SystemExit(f"Cannot traverse through non-container at {part!r}.")
    return current


def normalize_item(value: Any, item_id: str | None = None) -> Any:
    if item_id and isinstance(value, dict) and "id" not in value:
        result = dict(value)
        result["id"] = item_id
        return result
    return value


def find_item(items: list[Any], item_id: str) -> tuple[int, dict[str, Any]]:
    for index, item in enumerate(items):
        if isinstance(item, dict) and item.get("id") == item_id:
            return index, item
    raise SystemExit(f"List item with id {item_id!r} was not found.")


def op_set(slots: dict[str, Any], op: dict[str, Any], path: str) -> str:
    parent, key = get_parent(slots, path)
    if isinstance(parent, dict):
        parent[key] = op.get("value")
    elif isinstance(parent, list):
        parent[int(key)] = op.get("value")
    else:
        raise SystemExit(f"Cannot set value at {path}.")
    return path


def op_append_item(slots: dict[str, Any], op: dict[str, Any], path: str) -> str:
    target = get_value(slots, path, default=[])
    if not isinstance(target, list):
        raise SystemExit(f"append_item target is not a list: {path}")
    target.append(normalize_item(op.get("value"), op.get("id")))
    return path


def op_replace_item(slots: dict[str, Any], op: dict[str, Any], path: str) -> str:
    target = get_value(slots, path)
    if not isinstance(target, list):
        raise SystemExit(f"replace_item target is not a list: {path}")
    index, _ = find_item(target, str(op.get("id")))
    target[index] = normalize_item(op.get("value"), op.get("id"))
    return f"{path}/{op.get('id')}"


def op_replace_item_field(slots: dict[str, Any], op: dict[str, Any], path: str) -> str:
    target = get_value(slots, path)
    if not isinstance(target, list):
        raise SystemExit(f"replace_item_field target is not a list: {path}")
    _, item = find_item(target, str(op.get("id")))
    field = str(op.get("field") or "")
    if not field:
        raise SystemExit("replace_item_field requires field.")
    item[field] = op.get("value")
    return f"{path}/{op.get('id')}/{field}"


def op_remove_item(slots: dict[str, Any], op: dict[str, Any], path: str) -> str:
    target = get_value(slots, path)
    if not isinstance(target, list):
        raise SystemExit(f"remove_item target is not a list: {path}")
    index, _ = find_item(target, str(op.get("id")))
    target.pop(index)
    return f"{path}/{op.get('id')}"


OP_HANDLERS = {
    "set": op_set,
    "append_item": op_append_item,
    "replace_item": op_replace_item,
    "replace_item_field": op_replace_item_field,
    "remove_item": op_remove_item,
}


def apply_op(slots: dict[str, Any], op: dict[str, Any]) -> str:
    action = str(op.get("op") or "")
    path = str(op.get("path") or "")
    handler = OP_HANDLERS.get(action)
    if not handler:
        raise SystemExit(f"Unsupported update operation: {action}")
    return handler(slots, op, path)


def apply_patch(slots: dict[str, Any], patch: dict[str, Any], now: str) -> tuple[dict[str, Any], dict[str, Any]]:
    current = int(slots.get("revision") or 1)
    base = int(patch.get("base_revision") or 0)
    if base != current:
        raise SystemExit(f"Patch base_revision {base} does not match current revision {current}.")
    updated = deepcopy(slots)
    changed_paths = [apply_op(updated, op) for op in list(patch.get("ops") or [])]
    next_revision = current + 1
    updated["revision"] = next_revision
    history = list(updated.get("revision_history") or [])
    entry = {
        "revision": next_revision,
        "updated_at": now,
        "reason": str(patch.get("reason") or "No reason recorded."),
        "changed_paths": changed_paths,
    }
    history.append(entry)
    updated["revision_history"] = history
    return updated, entry


def append_change_log(path: Path, patch: dict[str, Any], slots: dict[str, Any], updated: dict[str, Any], history_entry: dict[str, Any], now: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "artifact": patch.get("artifact") or updated.get("template_id"),
            "from_revision": int(slots.get("revision") or 1),
            "to_revision": updated["revision"],
            "reason": history_entry["reason"],
            "ops_count": len(list(patch.get("ops") or [])),
            "changed_paths": history_entry["changed_paths"],
            "updated_at": now,
        }, ensure_ascii=False, sort_keys=True) + "\n")


def render_updated_slots(updated: dict[str, Any], patch: dict[str, Any], output: Path, render_output: Path) -> None:
    template_id = str(updated.get("template_id") or patch.get("template_id") or "")
    rendered = render_governance_artifact.render(updated, template_id, output.name)
    render_output.parent.mkdir(parents=True, exist_ok=True)
    render_output.write_text(rendered, encoding="utf-8")


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SystemExit(f"{label} must be a JSON object.")
    return value


def maybe_append_change_log(args: argparse.Namespace, patch: dict[str, Any], slots: dict[str, Any], updated: dict[str, Any], history_entry: dict[str, Any], now: str) -> None:
    if args.change_log:
        append_change_log(args.change_log, patch, slots, updated, history_entry, now)


def maybe_render(args: argparse.Namespace, patch: dict[str, Any], updated: dict[str, Any], output: Path) -> None:
    if args.render_output:
        render_updated_slots(updated, patch, output, args.render_output)


def optional_path(path: Path | None) -> str | None:
    return str(path) if path else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply a small update patch to a Project Governor artifact slot file.")
    parser.add_argument("--input", type=Path, required=True, help="Existing slot JSON file.")
    parser.add_argument("--patch", type=Path, required=True, help="Domain update patch JSON file.")
    parser.add_argument("--output", type=Path, help="Updated slot JSON output. Defaults to --input.")
    parser.add_argument("--render-output", type=Path, help="Optional Markdown output to regenerate.")
    parser.add_argument("--change-log", type=Path, help="Optional JSONL change log path.")
    parser.add_argument("--now", default=None, help="Timestamp override for deterministic tests.")
    args = parser.parse_args()

    slots = require_object(load_json(args.input), "Slot input")
    patch = require_object(load_json(args.patch), "Patch input")
    now = args.now if args.now else utc_now()
    updated, history_entry = apply_patch(slots, patch, now)
    output = args.output if args.output else args.input
    write_json(output, updated)
    maybe_append_change_log(args, patch, slots, updated, history_entry, now)
    maybe_render(args, patch, updated, output)
    print(json.dumps({
        "status": "updated",
        "schema": "project-governor-artifact-update-result-v1",
        "input": str(args.input),
        "output": str(output),
        "render_output": optional_path(args.render_output),
        "from_revision": int(slots.get("revision") or 1),
        "to_revision": updated["revision"],
        "changed_paths": history_entry["changed_paths"],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
