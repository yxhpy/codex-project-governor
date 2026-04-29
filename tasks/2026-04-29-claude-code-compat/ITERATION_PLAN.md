# Claude Code Compatibility Adapter

Date: 2026-04-29

## Request

Add Claude Code compatibility for Project Governor in one implementation pass, after the prior research concluded that Claude Code now has native plugin, skills, commands, agents, hooks, MCP, `CLAUDE.md`, and marketplace surfaces.

## Route

- Intended route: `standard_feature`
- Router output: `test_only` with low confidence because the request mentioned tests.
- Manual correction: this changes plugin distribution, templates, docs, release metadata, and tests, so it is not test-only.

## Existing Patterns Reused

- Keep the existing Codex plugin manifest at `.codex-plugin/plugin.json`.
- Add parallel runtime surfaces instead of replacing Codex surfaces.
- Reuse existing `skills/*/SKILL.md` workflows and deterministic Python scripts from plugin root.
- Reuse `templates/` for target-project governance payloads.
- Reuse `tests/selftest.py` and focused `tests/test_*.py` unittest style.
- Reuse `releases/FEATURE_MATRIX.json` and `releases/MIGRATIONS.json` for upgrade visibility.

## Expected Changes

- Add Claude Code plugin manifest and adapter files:
  - `.claude-plugin/plugin.json`
  - `claude/skills/project-governor/SKILL.md`
  - `claude/commands/*.md`
  - `claude/agents/*.md`
  - `claude/hooks/hooks.json`
  - `claude/hooks/project_governor_claude_hook.py`
- Add marketplace and compatibility docs:
  - `examples/claude-marketplace/.claude-plugin/marketplace.json`
  - `docs/compat/CLAUDE_CODE.md`
- Add target-project Claude instruction template:
  - `templates/CLAUDE.md`
- Update metadata and docs for version `6.2.0`.
- Add or update tests for manifest shape, Claude assets, hooks, marketplace, template init, and migration planning.

## Files Not To Change

- Do not rewrite existing `skills/*/SKILL.md` workflows.
- Do not change deterministic JSON output schemas except additive release metadata.
- Do not add package manifests, lockfiles, or third-party dependencies.
- Do not remove or rename existing Codex `.codex/` assets.

## New File Justification

Claude Code has different manifest, agent, command, and hook schemas. New adapter files keep those schemas separate from Codex schemas and avoid breaking current Codex installations.

## Test Plan

- `python3 tests/test_claude_code_compat.py`
- `python3 tests/selftest.py`
- `python3 tests/test_plugin_upgrade_migrator.py`
- `python3 tests/test_harness_v6.py`
- `python3 -m compileall tools skills tests claude`
- `claude plugin validate .`
- `make test`

## Risks

- Claude Code plugin schema can drift; mitigate with `claude plugin validate .`.
- Dual Codex/Claude surfaces can drift; mitigate with tests comparing Claude agents to `.codex/agents/*.toml` names and descriptions.
- Claude project `CLAUDE.md` can grow context cost; keep the template as a thin `@AGENTS.md` import.

## Rollback Path

Remove the Claude adapter files, `templates/CLAUDE.md`, and v6.2.0 release metadata; restore manifest version and docs to v6.1.0.
