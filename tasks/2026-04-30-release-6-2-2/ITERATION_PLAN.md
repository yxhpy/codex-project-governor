# Iteration Plan: Release 6.2.2

## Request

Publish a Project Governor patch release for the diagnostics baseline cleanup and follow-up release consistency fixes.

## Upgrade Advisory

Use `tasks/2026-04-30-release-6-2-2/UPGRADE_ADVISORY_INPUT.json` with `upgrade-advisor`. The intended user choice is `upgrade_now` because the user explicitly requested a new release and the candidate is a low-risk patch version.

## Existing Patterns Reused

- `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` remain the plugin metadata sources.
- `releases/FEATURE_MATRIX.json`, `releases/<version>.md`, and `docs/upgrades/UPGRADE_REGISTER.md` remain the release and upgrade ledgers.
- Existing version contract tests in `tests/selftest.py`, `tests/test_harness_v6.py`, and `tests/test_claude_code_compat.py` remain the release metadata checks.
- Existing no-migration patch-release pattern is reused because no initialized-project file migration is required.

## Expected Changes

- Bump Codex and Claude plugin metadata from `6.2.1` to `6.2.2`.
- Add `releases/6.2.2.md` and a `6.2.2` entry in `releases/FEATURE_MATRIX.json`.
- Update README install/update snippets, current release docs, marketplace example refs, tests, and memory/current-phase docs to `6.2.2`.
- Record the applied upgrade in `docs/upgrades/UPGRADE_REGISTER.md`.

## Files Not To Change

- Do not add dependencies, lockfiles, package manifests, or runtime services.
- Do not change deterministic helper JSON output schemas.
- Do not add `releases/MIGRATIONS.json` entries unless a project migration becomes required.
- Do not rewrite historical release notes for older versions.

## Risks

- Version drift across Codex, Claude, README, marketplace examples, tests, and feature matrix.
- A patch release could accidentally imply project migration if feature metadata is marked incorrectly.
- Existing dirty worktree contains broad diagnostics cleanup; release edits must not revert or obscure those changes.

## Rollback

Revert the `6.2.2` version bump, release note, feature-matrix entry, upgrade-register row, and test/doc version assertions.
