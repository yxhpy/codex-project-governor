# Pattern Reuse Plan

## Existing Patterns Reused

- Reused `skills/CATALOG.json` as the machine-readable source for skill audience and documentation grouping.
- Reused `tools/analyze_skill_catalog.py` as the deterministic catalog health CLI instead of adding a new command.
- Reused `tests/test_skill_catalog_analyzer.py` for analyzer regression coverage.
- Reused README visibility grouping instead of changing skill names, skill folders, plugin metadata, or template payloads.

## New Patterns

No new runtime pattern, dependency, service, template path, or skill directory was introduced. The only new metadata pattern is optional `consolidation_groups` inside `skills/CATALOG.json`, documented in the API contract.

## Not Reused

No external parser or package was added because the existing analyzer is standard-library Python.
