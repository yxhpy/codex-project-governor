# Iteration Plan: Release 6.2.1

## Request

Prepare a patch release for the skill-entrypoint consolidation, routing cleanup, compact default prompts, and analyzer quality work completed in this session.

## Existing Patterns Reused

- `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` remain the plugin metadata sources.
- `releases/FEATURE_MATRIX.json` and `releases/<version>.md` remain the release capability ledger.
- `docs/upgrades/UPGRADE_REGISTER.md` remains the upgrade decision ledger after `upgrade-advisor` advisory.
- `tests/selftest.py`, `tests/test_harness_v6.py`, and `tests/test_claude_code_compat.py` remain the version and metadata contract checks.

## Expected Changes

- Bump Codex and Claude plugin manifests from `6.2.0` to `6.2.1`.
- Update install/update README snippets and default prompt version text to `v6.2.1`.
- Add a `6.2.1` feature-matrix entry for the skill catalog, docs-only routing, compact default prompts, and analyzer module split.
- Add `releases/6.2.1.md` and record the applied upgrade in `docs/upgrades/UPGRADE_REGISTER.md`.
- Update tests that intentionally assert the current release version and marketplace ref.

## Files Not To Change

- Do not alter migration metadata unless a project migration is required.
- Do not rename, delete, or deprecate any skill.
- Do not add package manifests, lockfiles, dependencies, runtime services, or application code.
- Do not rewrite existing release history for `6.2.0`.

## Test Plan

- JSON validation for updated manifests and feature matrix.
- Version contract tests: `tests/selftest.py`, `tests/test_harness_v6.py`, `tests/test_claude_code_compat.py`.
- Migration regression test: `tests/test_plugin_upgrade_migrator.py`.
- Skill catalog analyzer and analyzer unit tests.
- Python syntax compileall for `tools`, `skills`, `tests`, and `claude`.
- Engineering standards, diff whitespace, full `make test`, route guard, quality gate, and merge readiness.

## Risks

- Version-only changes can drift across Codex, Claude, marketplace, README, and tests. Grep-based verification will check no unintended current-release `6.2.0` references remain outside historical release and migration records.
- A patch release without project migration should not add `releases/MIGRATIONS.json` entries.

## Rollback

Revert the version bump, remove `releases/6.2.1.md`, remove the `6.2.1` feature-matrix and upgrade-register rows, and restore tests to assert `6.2.0`.
