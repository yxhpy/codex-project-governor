# Code Style

## Python CLI Scripts

- Use Python standard library modules unless a decision record approves otherwise.
- Start scripts with `#!/usr/bin/env python3` when executable.
- Use `from __future__ import annotations`.
- Use `argparse` for CLI arguments.
- Use `pathlib.Path` for filesystem paths.
- Use typed functions and small dataclasses where structured results help.
- End executable scripts with `raise SystemExit(main())`.
- Emit JSON with `indent=2` and `ensure_ascii=False` when producing structured reports.

## Naming

- Use `snake_case` for functions, variables, and module-level helpers.
- Use `UPPER_SNAKE_CASE` for constants.
- Use `PascalCase` for dataclasses.
- Name test methods with `test_*`.

## Error Handling

- Fail fast for missing template roots or invalid required inputs.
- Deterministic guard scripts should return structured JSON and non-zero exit for blocking findings.
- Do not add broad exception swallowing around validation logic.

## Markdown

- Use ATX headings.
- Keep sections short and declarative.
- Use fenced code blocks for commands and prompt examples.
- Use tables for registries, decision summaries, and report shapes.

## Evidence

- `tools/init_project.py`
- `skills/convention-miner/scripts/detect_repo_conventions.py`
- `skills/implementation-guard/scripts/check_iteration_compliance.py`
- `skills/style-drift-check/scripts/check_style_drift.py`
- `skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py`
- `skills/memory-compact/scripts/classify_memory_items.py`
- `tests/selftest.py`
