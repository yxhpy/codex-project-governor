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
CLASSIFICATION_RULES = [
    ("command_learning", ["command failed", "exit code", "returncode", "approval required", "permission denied", "命令失败", "执行错误"]),
    ("decision", [" adr", "pdr", "we decided"]),
    ("repeated_mistake", ["repeated mistake", "agent keeps", "codex keeps"]),
    ("risk", ["risk register"]),
    ("open_question", ["unknown", "unclear"]),
    ("durable_fact", ["stable", "durable"]),
    ("stale_item", ["superseded", "deprecated"]),
]


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


def has_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def prefix_classification(lower: str) -> str | None:
    prefixes = {
        "decision:": "decision",
        "risk:": "risk",
        "question:": "open_question",
        "fact:": "durable_fact",
        "stale:": "stale_item",
    }
    return next((classification for prefix, classification in prefixes.items() if lower.startswith(prefix)), None)


def classify(text: str) -> str:
    lower = text.lower()
    if SECRET.search(text):
        return "secret_or_sensitive"
    prefixed = prefix_classification(lower)
    if prefixed:
        return prefixed
    if "?" in text:
        return "open_question"
    for classification, terms in CLASSIFICATION_RULES:
        if has_any(lower, terms):
            return classification
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
