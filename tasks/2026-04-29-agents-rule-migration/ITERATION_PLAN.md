# Iteration Plan: AGENTS Rule Migration Visibility

## User request

Ensure mandatory Project Governor rules added after initialization are visible to users' `AGENTS.md` during plugin upgrades.

## Existing behavior

`templates/AGENTS.md` is copied during initialization and tracked in `.project-governor/INSTALL_MANIFEST.json` with `three_way_merge` policy. `plugin-upgrade-migrator` only plans `AGENTS.md` review when a release migration explicitly includes that file, so later mandatory template rules can be missed by already initialized projects.

## Upgrade advisory

| Package / Tool | Current | Candidate | Behind / isolated by | Requirement relevance | Risk | Recommendation | Why |
|---|---:|---:|---:|---|---|---|---|
| Project Governor plugin | 6.0.2 | 6.0.3 | one patch release | required by user request | low: patch release for migration planning, documentation, and tests; no dependencies | upgrade_required | User requested publishing the AGENTS.md rule-template drift fix as a new version. |

Decision: `upgrade_now`.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
|---|---|---|
| Install manifest hash comparison | `tools/init_project.py`, `skills/plugin-upgrade-migrator/scripts/inspect_installation.py` | Compare installed template hashes with current template hashes. |
| Three-way/manual review for `AGENTS.md` | `tools/init_project.py`, `skills/plugin-upgrade-migrator/SKILL.md` | Keep user-modified `AGENTS.md` out of automatic overwrite paths. |
| Deterministic unittest coverage | `tests/test_plugin_upgrade_migrator.py` | Add regression coverage for rule-template drift planning. |

## Files expected to change

- `skills/plugin-upgrade-migrator/scripts/plan_migration.py`
- `skills/plugin-upgrade-migrator/SKILL.md`
- `.codex-plugin/plugin.json`
- `CHANGELOG.md`
- `releases/FEATURE_MATRIX.json`
- `releases/6.0.3.md`
- `templates/AGENTS.md`
- `AGENTS.md`
- `templates/docs/upgrades/PLUGIN_UPGRADE_POLICY.md`
- `README.md`
- `README.zh-CN.md`
- `docs/architecture/API_CONTRACTS.md`
- `docs/memory/RISK_REGISTER.md`
- `tests/test_plugin_upgrade_migrator.py`

## Files not to change

- `.codex-plugin/plugin.json`
- `tools/init_project.py`
- dependency manifests or lockfiles
- template paths under `templates/`

## New files

| File | Why existing files cannot cover it |
|---|---|
| `tasks/2026-04-29-agents-rule-migration/ITERATION_PLAN.md` | Required for a non-trivial script, policy, and test change. |
| `releases/6.0.3.md` | Versioned release notes are required for the new patch release. |

## Dependencies

No new dependencies expected unless explicitly approved.

## Tests

- `python3 tests/test_plugin_upgrade_migrator.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`

## Risks

- Upgrade plans could become noisy if every template drift is surfaced. Limit automatic drift detection to rule-bearing `AGENTS.md`.
- Automatic application must not overwrite user-modified `AGENTS.md`; preserve existing `three_way_merge` classification.

## Rollback

Revert this task's changed files. Existing explicit migrations will continue to work as before, but `AGENTS.md` drift will again require explicit migration entries.
