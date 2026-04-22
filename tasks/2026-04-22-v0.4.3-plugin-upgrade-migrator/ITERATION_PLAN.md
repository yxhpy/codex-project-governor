# Iteration Plan: v0.4.3 Plugin Upgrade Migrator

## Request

Upgrade and publish Project Governor using `/Users/yxhpy/Downloads/codex-project-governor-v0.4.3-plugin-upgrade-migrator.patch`.

## Upgrade Advisory

| Package / Tool | Current | Candidate | Behind / isolated by | Requirement relevance | Risk | Recommendation | Why |
|---|---:|---:|---:|---|---|---|---|
| Project Governor plugin | 0.4.2 | 0.4.3 | one patch release by local patch evidence | required by user request | medium: plugin metadata, one new skill, release metadata, install manifest template, migration helper JSON contracts, and tests change | upgrade_required | User requested continued upgrade and publish; the patch adds safe plugin upgrade planning without new dependencies. |

Decision: `upgrade_now`.

## Existing Patterns Reused

- Skill workflows live under `skills/<skill>/SKILL.md`.
- Deterministic helpers live under `skills/<skill>/scripts/` and use Python standard library only.
- Example inputs live under `examples/*.json`.
- Copied governance payloads live under `templates/`.
- Public plugin metadata starts at `.codex-plugin/plugin.json`.
- Tests use standard-library `unittest`.

## Expected Changes

- Add `plugin-upgrade-migrator` skill and deterministic inspect/compare/plan/apply helpers.
- Add release metadata under `releases/`.
- Add install manifest and plugin upgrade policy templates.
- Add changelog and README/Chinese usage updates.
- Update API contracts, upgrade register, Makefile, and selftests.
- Publish `v0.4.3` after validation.

## Files Not To Change

- Do not add dependencies, package manifests, lockfiles, services, or runtimes.
- Do not change initializer JSON output.
- Do not overwrite existing release history or prior release tags.

## New File Justification

The migrator needs a skill, helper scripts, release metadata, migration metadata, install manifest template, policy docs, examples, and tests. These are plugin governance surfaces, not application runtime code.

## Tests

- `python3 tests/selftest.py`
- `python3 tests/test_smart_routing_guard.py`
- `python3 tests/test_subagent_activation.py`
- `python3 tests/test_plugin_upgrade_migrator.py`
- `python3 -m compileall tools skills tests`
- `make test`
- `python3 tools/init_project.py --mode existing --target <tmpdir> --json`

## Risks

- Patch tried to replace README with a short version; manually preserve the full README and add v0.4.3 content.
- Helper scripts must not overwrite user-modified project governance files blindly.
- New migration JSON contracts must be documented in API contracts and validated by tests.

## Rollback

Revert this task's changed files and restore `.codex-plugin/plugin.json` version `0.4.2`.
