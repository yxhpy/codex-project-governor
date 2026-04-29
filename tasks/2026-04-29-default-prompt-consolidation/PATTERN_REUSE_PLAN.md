# Pattern Reuse Plan

## Existing Patterns Reused

- Reused `.codex-plugin/plugin.json` as the single source for Codex plugin UI default prompts.
- Reused README skill grouping as the user-facing model for prompt scenarios.
- Reused `tests/selftest.py` for plugin manifest contract checks.
- Reused `docs/architecture/API_CONTRACTS.md` for public metadata contract documentation.

## New Patterns

No new runtime pattern, dependency, service, template path, or skill directory was introduced. The change adds a policy constraint: default prompts should stay compact and scenario-level.

## Not Reused

No extra manifest validator was added because `tests/selftest.py` already validates `.codex-plugin/plugin.json`.
