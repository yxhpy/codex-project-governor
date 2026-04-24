# Iteration Plan: v0.5.0 GPT-5.5 Auto Orchestration

## Request

Apply the latest Project Governor patch from Downloads, upgrade the plugin, and publish a new version.

## Upgrade Advisory

| Package / Tool | Current | Candidate | Behind / isolated by | Requirement relevance | Risk | Recommendation | Why |
|---|---:|---:|---:|---|---|---|---|
| Project Governor plugin | 0.4.7 | 0.5.0 | 1 minor release | required | medium | upgrade_required | The user explicitly selected the latest Downloads patch as the upgrade source and asked to publish a new version. |

Decision: `upgrade_now`.

Evidence:

- `/Users/yxhpy/Downloads/codex-project-governor-v0.5.0-gpt55-auto-orchestration.patch`
- `.codex-plugin/plugin.json`
- `releases/FEATURE_MATRIX.json`
- `docs/upgrades/UPGRADE_REGISTER.md`

## Existing Patterns Reused

- Add release metadata beside prior `releases/0.4.x.md` files.
- Keep deterministic helpers dependency-free Python scripts under `skills/*/scripts/`.
- Add target-project copied assets only under `templates/`.
- Add plugin-owned source material under `managed-assets/`.
- Update `tests/selftest.py` and `Makefile` when adding a new test module.

## Expected Changes

- Add `gpt55-auto-orchestrator` and `context-indexer` skills.
- Add deterministic runtime routing and context index scripts.
- Add project-owned runtime template under `templates/.project-governor/runtime/`.
- Add v0.5.0 release metadata and docs.
- Update plugin manifest, README files, changelog, API contracts, feature matrix, upgrade register, and self-test expectations.

## Files Not To Change

- No application code exists in this repository.
- Do not add dependencies or package manifests.
- Do not copy plugin-global `.codex/agents` into target-project templates.
- Do not commit generated `__pycache__` or `.pyc` files from the patch.

## Validation Plan

- `python3 tests/test_gpt55_auto_orchestration.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`
- `make test`
- `python3 tools/init_project.py --mode existing --target <tmpdir> --json`

## Risks

- GPT-5.5 model routing claims may drift if model availability changes.
- New deterministic JSON outputs must be documented in API contracts.
- Project migrations must remain project-owned and opt-in; plugin-global assets must not be copied into target projects.

## Rollback

Revert the v0.5.0 commit and delete tag/release if publication fails before adoption.
