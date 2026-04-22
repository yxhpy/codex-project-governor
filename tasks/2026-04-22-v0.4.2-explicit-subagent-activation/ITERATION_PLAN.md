# Iteration Plan: v0.4.2 Explicit Subagent Activation

## Request

Continue upgrading and publishing Project Governor using `/Users/yxhpy/Downloads/codex-project-governor-v0.4.2-explicit-subagent-activation.patch`.

## Upgrade Advisory

| Package / Tool | Current | Candidate | Behind / isolated by | Requirement relevance | Risk | Recommendation | Why |
|---|---:|---:|---:|---|---|---|---|
| Project Governor plugin | 0.4.1 | 0.4.2 | one patch release by local patch evidence | required by user request | medium: plugin metadata, project-scoped `.codex/agents`, one new skill, deterministic selector JSON, copied templates, and tests change | upgrade_required | User requested continued upgrade and publish; the patch adds explicit subagent activation without new dependencies. |

Decision: `upgrade_now`.

## Existing Patterns Reused

- Skill workflows live under `skills/<skill>/SKILL.md`.
- Deterministic helpers live under `skills/<skill>/scripts/` and use Python standard library only.
- Example inputs live under `examples/*.json`.
- Copied governance payloads live under `templates/`.
- Project-scoped Codex config and prompts live under `.codex/` and `templates/.codex/`.
- Public plugin metadata starts at `.codex-plugin/plugin.json`.
- Self-tests and targeted tests validate deterministic helper behavior.

## Expected Changes

- Add project-scoped `.codex/agents/*.toml` and copied template equivalents.
- Add `subagent-activation` skill and deterministic `select_subagents.py`.
- Update existing workflows to state when `subagent-activation` is automatic.
- Add subagent activation policy, prompt, examples, and focused tests.
- Bump plugin metadata and docs to `0.4.2`.
- Record the upgrade decision.

## Files Not To Change

- Do not add dependencies, package manifests, lockfiles, services, or runtimes.
- Do not change initializer JSON output.
- Do not remove v0.4.1 route guard fields or compatibility behavior.

## New File Justification

`subagent-activation` requires project-scoped role definitions, a reusable selector, example fixtures, copied template config, policy docs, a research brief, and tests. These are plugin/template surfaces, not application runtime code.

## Tests

- `python3 tests/selftest.py`
- `python3 tests/test_smart_routing_guard.py`
- `python3 tests/test_subagent_activation.py`
- `python3 -m compileall tools skills tests`
- `make test`
- `python3 tools/init_project.py --mode existing --target <tmpdir> --json`

## Risks

- The patch was generated against a compressed baseline, so existing formatted files need manual rebase.
- Subagent docs must not imply multiple write agents can modify overlapping production code.
- `micro_patch` must remain fast and not spawn subagents by default.

## Rollback

Revert this task's changed files and restore `.codex-plugin/plugin.json` version `0.4.1`.
