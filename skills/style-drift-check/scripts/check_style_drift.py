#!/usr/bin/env python3
"""Detect simple style-drift indicators from JSON input.

Input JSON fields:
- new_components: list of component names introduced by the change
- registered_components: list of component names in COMPONENT_REGISTRY.md
- raw_colors: list of raw color literals found in changed files
- new_style_systems: list of style systems or libraries introduced
- approved_style_systems: list of approved style systems
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

RAW_COLOR = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b|rgba?\(")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check(data: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    new_components = set(data.get("new_components", []))
    registered = set(data.get("registered_components", []))
    unregistered = sorted(new_components - registered)
    if unregistered:
        findings.append({
            "severity": "blocking",
            "type": "unregistered_components",
            "items": unregistered,
            "message": "New components must be added to COMPONENT_REGISTRY.md or replaced by existing components."
        })

    raw_colors = [c for c in data.get("raw_colors", []) if RAW_COLOR.search(str(c))]
    if raw_colors:
        findings.append({
            "severity": "blocking",
            "type": "raw_color_literals",
            "items": raw_colors,
            "message": "Use existing design tokens instead of raw color literals."
        })

    new_style_systems = set(data.get("new_style_systems", []))
    approved = set(data.get("approved_style_systems", []))
    unapproved_systems = sorted(new_style_systems - approved)
    if unapproved_systems:
        findings.append({
            "severity": "blocking",
            "type": "unapproved_style_systems",
            "items": unapproved_systems,
            "message": "Do not introduce a new styling system without a decision record."
        })

    return {"status": "fail" if findings else "pass", "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check style drift from a JSON input file.")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = check(load_json(args.input))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
