# Iteration Plan: v0.4.1 Smart Routing Guard

## Request

Upgrade Project Governor to `0.4.1` using `/Users/yxhpy/Downloads/codex-project-governor-v0.4.1-smart-routing-guard.patch`.

## Upgrade Advisory

| Package / Tool | Current | Candidate | Behind / isolated by | Requirement relevance | Risk | Recommendation | Why |
|---|---:|---:|---:|---|---|---|---|
| Project Governor plugin | 0.4.0 | 0.4.1 | one patch release by local patch evidence | required by user request | medium: plugin metadata, one new skill, deterministic routing JSON, templates, and tests change | upgrade_required | User selected the 4.1 upgrade; the patch adds smart routing guardrails without new dependencies. |

Decision: `upgrade_now`.

## Existing Patterns Reused

- Skill workflows live under `skills/<skill>/SKILL.md`.
- Deterministic helpers live under `skills/<skill>/scripts/` and use Python standard library only.
- Example inputs live under `examples/*.json`.
- Copied governance payloads live under `templates/`.
- Public plugin metadata starts at `.codex-plugin/plugin.json`.
- Self-tests and targeted test scripts validate deterministic helper behavior.

## Expected Changes

- Add `route-guard` skill and deterministic route guard script.
- Extend `task-router` with `micro_patch`, negative constraint parsing, route guard requirements, and escalation metadata.
- Extend `quality-gate` to optionally execute route guard while preserving v0.4.0 output fields.
- Add route guard examples, templates, policy docs, and tests.
- Bump plugin metadata and documentation to `0.4.1`.
- Record the upgrade decision.

## Files Not To Change

- Do not add dependencies, manifests, lockfiles, services, or runtimes.
- Do not change initializer JSON output.
- Do not replace existing 0.4.0 routing or quality-gate JSON fields when additive compatibility is enough.

## New File Justification

`route-guard` requires a new skill, deterministic helper script, example fixtures, copied-template prompt/policy/report files, a research brief, and focused tests. These are plugin/template surfaces, not application code.

## Tests

- `python3 tests/selftest.py`
- `python3 tests/test_smart_routing_guard.py`
- `python3 -m compileall tools skills tests`
- `make test`
- `python3 tools/init_project.py --mode existing --target <tmpdir> --json`

## Risks

- The patch was generated against a simplified v0.4.0 baseline, so conflict files must be manually rebased.
- `task-router` output should gain route guard fields without breaking v0.4.0 tests.
- `quality-gate` should support route guard without removing existing `findings`, `commands`, and `repair_loop_required` fields.

## Rollback

Revert this task's changed files and restore `.codex-plugin/plugin.json` version `0.4.0`.
