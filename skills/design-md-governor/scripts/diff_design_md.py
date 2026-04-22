#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lint_design_md import lint_design_md


def token_group(result: dict[str, Any], group: str) -> dict[str, Any]:
    data = result.get("designSystem", {}).get(group, {})
    return data if isinstance(data, dict) else {}


def compare(before: Path, after: Path) -> dict[str, Any]:
    before_result = lint_design_md(before)
    after_result = lint_design_md(after)
    groups = ["colors", "typography", "rounded", "spacing", "components"]
    tokens: dict[str, Any] = {}
    for group in groups:
        old = token_group(before_result, group)
        new = token_group(after_result, group)
        tokens[group] = {
            "added": sorted(set(new) - set(old)),
            "removed": sorted(set(old) - set(new)),
            "modified": sorted(k for k in set(old) & set(new) if old[k] != new[k]),
        }
    regression = after_result["summary"]["errors"] > before_result["summary"]["errors"] or after_result["summary"]["warnings"] > before_result["summary"]["warnings"]
    return {"before": str(before), "after": str(after), "tokens": tokens, "before_summary": before_result["summary"], "after_summary": after_result["summary"], "regression": regression}


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff two DESIGN.md files.")
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    result = compare(args.before, args.after)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["regression"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
