from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


def sha256_path(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_version(version: str) -> tuple[int, int, int]:
    match = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", str(version).strip())
    if not match:
        raise ValueError(f"invalid version: {version!r}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def version_between(version: str, current: str, target: str) -> bool:
    return parse_version(current) < parse_version(version) <= parse_version(target)


def operation_policy(path: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    if path.startswith("docs/memory/"):
        return "append_only"
    if path.startswith("docs/decisions/"):
        return "never_overwrite"
    if path == "AGENTS.md":
        return "three_way_merge"
    if path == ".codex/config.toml":
        return "merge_toml"
    if path.startswith(".codex/agents/"):
        return "merge_by_agent_name"
    if path.startswith(".codex/prompts/") or path.startswith("docs/conventions/") or path.startswith("tasks/_template/"):
        return "three_way_merge"
    return "add_if_missing"
