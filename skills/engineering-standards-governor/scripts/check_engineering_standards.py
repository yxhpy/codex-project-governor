#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from standards_core import Thresholds
from standards_checks import check, format_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Project Governor engineering standards.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--scope", choices=["all", "diff"])
    parser.add_argument("--diff-base")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    parser.add_argument("--file-warn-lines", type=int, default=Thresholds.file_warn_lines)
    parser.add_argument("--file-fail-lines", type=int, default=Thresholds.file_fail_lines)
    parser.add_argument("--function-warn-lines", type=int, default=Thresholds.function_warn_lines)
    parser.add_argument("--function-fail-lines", type=int, default=Thresholds.function_fail_lines)
    parser.add_argument("--complexity-warn", type=int, default=Thresholds.complexity_warn)
    parser.add_argument("--complexity-fail", type=int, default=Thresholds.complexity_fail)
    args = parser.parse_args()

    thresholds = Thresholds(
        file_warn_lines=args.file_warn_lines,
        file_fail_lines=args.file_fail_lines,
        function_warn_lines=args.function_warn_lines,
        function_fail_lines=args.function_fail_lines,
        complexity_warn=args.complexity_warn,
        complexity_fail=args.complexity_fail,
    )
    scope = args.scope or ("diff" if args.diff_base else "all")
    result = check(args.project, scope=scope, diff_base=args.diff_base, thresholds=thresholds)
    if args.format == "text":
        print(format_text(result))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
