# Pattern Reuse Plan

## Existing Patterns Reused

- Kept `tools/analyze_skill_catalog.py` as the stable CLI entrypoint.
- Reused the existing analyzer output schema, command-line flags, and text headings.
- Reused `tests/test_skill_catalog_analyzer.py` for behavior, drift, and regression coverage.
- Reused `docs/architecture/API_CONTRACTS.md` for deterministic CLI contract documentation.

## New Patterns

No new dependency, runtime, service, or skill directory was introduced. The only structural change is splitting analyzer implementation into sibling stdlib-only helper modules under `tools/`.

## Not Reused

No package framework or argparse wrapper library was added. The CLI remains a direct Python script.
