# Iteration Plan: v0.4 Quality-Gated Acceleration

## Request

Apply the local v0.4 upgrade patch from `/Users/yxhpy/Downloads/codex-project-governor-add-quality-gated-acceleration-v0.4.patch`.

## Upgrade Advisory

| Package / Tool | Current | Candidate | Behind / isolated by | Requirement relevance | Risk | Recommendation | Why |
|---|---:|---:|---:|---|---|---|---|
| Project Governor plugin | 0.3.1 | 0.4.0 | one minor plugin release by local patch evidence | required by user-provided v0.4 patch | medium: public plugin metadata, skill catalog, copied template files, and self-tests change | upgrade_required | User selected the v0.4 local patch; the change adds quality-gated acceleration workflows without new dependencies. |

Decision: `upgrade_now`.

## Existing Patterns Reused

- Skill workflows live under `skills/<skill>/SKILL.md`.
- Deterministic helper scripts live under `skills/<skill>/scripts/` and use only Python standard library.
- Example inputs live under `examples/*.json`.
- Copied governance payloads live under `templates/`.
- Public plugin metadata starts at `.codex-plugin/plugin.json`.
- Validation is centralized in `tests/selftest.py`.

## Expected Changes

- Update plugin metadata and README positioning for v0.4 quality-gated acceleration.
- Add focused acceleration skills, helper scripts, examples, prompts, quality docs, and task templates from the patch.
- Manually rebase drifted edits in `.codex-plugin/plugin.json`, `templates/AGENTS.md`, `templates/docs/conventions/CONVENTION_MANIFEST.md`, and `tests/selftest.py`.
- Update upgrade register for the v0.4 decision.

## Files Not To Change

- Do not add package manifests, lockfiles, dependencies, services, or runtimes.
- Do not change initializer output schemas except template file coverage validated by tests.
- Do not rewrite existing skill families.

## New File Justification

Each new skill, prompt, example, quality policy, and task-template file is a plugin or copied-template surface required by the v0.4 acceleration workflow. No new runtime dependency is introduced.

## Tests

- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`
- `make test`
- `python3 tools/init_project.py --mode existing --target <tmpdir> --json`

## Risks

- Patch was authored against v0.3.0 while the repo is already v0.3.1.
- Skill count, manifest version, docs, templates, and tests must stay in sync.
- New deterministic scripts must expose stable importable functions and CLI JSON output.

## Rollback

Revert this task's changed files and restore `.codex-plugin/plugin.json` version `0.3.1`.
