# Iteration Plan: Skill Catalog Analyzer Split

## Request

Continue optimizing by removing the remaining engineering standards warning from `tools/analyze_skill_catalog.py`.

## Existing Patterns Reused

- Keep `tools/analyze_skill_catalog.py` as the deterministic CLI entrypoint.
- Reuse the existing analyzer functions and output schema without changing behavior.
- Reuse `tests/test_skill_catalog_analyzer.py` as the regression suite for JSON/text output and failure cases.
- Reuse `docs/architecture/API_CONTRACTS.md` for CLI contract documentation.

## Expected Changes

- Split analysis logic into `tools/skill_catalog_analysis.py`.
- Split text rendering into `tools/skill_catalog_render.py`.
- Reduce `tools/analyze_skill_catalog.py` to a thin CLI wrapper.
- Add a focused test that all analyzer production files stay below the 400-line warning threshold.
- Update API contract documentation to note the CLI delegates to helper modules.

## Files Not To Change

- Do not change `skills/CATALOG.json` semantics.
- Do not change analyzer JSON fields or text output headings.
- Do not rename the CLI command.
- Do not add dependencies.

## Test Plan

- `python3 tools/analyze_skill_catalog.py --project . --format json --fail-on-issues`
- `python3 tools/analyze_skill_catalog.py --project . --format text --fail-on-issues`
- `python3 tests/test_skill_catalog_analyzer.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`
- `git diff --check`
- `python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --diff-base main`
- `make test`

## Risks

- Import path behavior can break when the CLI is run directly. The wrapper should import sibling modules in `tools/` using standard direct imports.
- Behavior drift is possible during mechanical extraction. Existing analyzer tests and analyzer JSON/text commands protect the output contract.

## Rollback

Move helper-module contents back into `tools/analyze_skill_catalog.py` and remove the new line-budget test.
