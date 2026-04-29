#!/usr/bin/env python3
"""Classify memory candidates into governance buckets.

Input may be either:
- JSON list of strings
- JSON object with an `items` list
- plain text with one item per line
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SECRET = re.compile(r"(api[_-]?key|secret|token|password|private[_-]?key)\s*[:=]", re.I)


def load_items(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    try:
        data: Any = json.loads(text)
        if isinstance(data, dict):
            data = data.get("items", [])
        if isinstance(data, list):
            return [str(item) for item in data]
    except json.JSONDecodeError:
        pass
    return [line.strip() for line in text.splitlines() if line.strip()]


def classify(text: str) -> str:
    lower = text.lower()
    if SECRET.search(text):
        return "secret_or_sensitive"
    if any(term in lower for term in ["command failed", "exit code", "returncode", "approval required", "permission denied", "命令失败", "执行错误"]):
        return "command_learning"
    if lower.startswith("decision:") or " adr" in lower or "pdr" in lower or "we decided" in lower:
        return "decision"
    if "repeated mistake" in lower or "agent keeps" in lower or "codex keeps" in lower:
        return "repeated_mistake"
    if lower.startswith("risk:") or "risk register" in lower:
        return "risk"
    if "?" in text or lower.startswith("question:") or "unknown" in lower or "unclear" in lower:
        return "open_question"
    if lower.startswith("fact:") or "stable" in lower or "durable" in lower:
        return "durable_fact"
    if lower.startswith("stale:") or "superseded" in lower or "deprecated" in lower:
        return "stale_item"
    return "temporary_note"


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify project memory candidates.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    out = [{"text": item, "classification": classify(item)} for item in load_items(args.input)]
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
