# Iteration Plan: Skill Catalog Resolved Candidates

## Request

Continue optimizing the skill surface by reducing analyzer noise after public README entrypoints have already been consolidated.

## Existing Patterns Reused

- `skills/CATALOG.json` is the source of truth for skill audience and documentation grouping metadata.
- `tools/analyze_skill_catalog.py` is a stdlib-only CLI that reports catalog health and advisory consolidation candidates.
- `tests/test_skill_catalog_analyzer.py` covers current catalog health, README grouping drift, and text/JSON output behavior.
- `docs/architecture/API_CONTRACTS.md` documents deterministic CLI output contracts.

## Expected Changes

- Add catalog-level declarations for consolidation groups that have already been handled in README grouping.
- Teach `tools/analyze_skill_catalog.py` to separate resolved consolidations from open consolidation candidates.
- Update analyzer tests to assert that resolved groups are reported separately and open candidates are not inflated by already-handled entrypoints.
- Update API contract documentation for the new optional catalog metadata and JSON output field.

## Files Not To Change

- Do not delete, rename, or deprecate any skill directory.
- Do not change `.codex-plugin/plugin.json` or `.claude-plugin/plugin.json`.
- Do not change deterministic helper dependencies.
- Do not change template payload paths.

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

- Public analyzer JSON output changes need documentation because downstream checks may read `summary.candidate_count`.
- Over-filtering candidates could hide real duplication risk, so only explicit catalog groups with `status: resolved` should suppress candidates.

## Rollback

Remove `consolidation_groups`, revert analyzer filtering, and restore tests to assert the previous candidate list.
