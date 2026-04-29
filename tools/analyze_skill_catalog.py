#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from skill_catalog_analysis import analyze
    from skill_catalog_render import render_text
except ModuleNotFoundError:  # pragma: no cover - supports package-style imports.
    from tools.skill_catalog_analysis import analyze
    from tools.skill_catalog_render import render_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Project Governor skill catalog metadata and consolidation candidates.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices={"json", "text"}, default="json")
    parser.add_argument("--min-overlap", type=float, default=0.42)
    parser.add_argument("--fail-on-issues", action="store_true")
    args = parser.parse_args()

    result = analyze(args.project.resolve(), args.min_overlap)
    if args.format == "text":
        print(render_text(result), end="")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.fail_on_issues and result["status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
