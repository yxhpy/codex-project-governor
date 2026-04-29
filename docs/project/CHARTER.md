# Project Charter

## Project identity

`codex-project-governor` is a Codex and Claude Code plugin for making repositories self-governing across agent sessions.

## Purpose

The project provides governance templates, Codex and Claude Code plugin surfaces, deterministic helper scripts, marketplace examples, user-level Git install/update support for local marketplaces, Harness v6.2.0 task routing, GPT-5.5-aware runtime planning, compact context indexing with `DOCS_MANIFEST.json` and section-level retrieval, governed memory search, session-learning ledgers for failed commands and stale memory, session state, evidence manifests, engineering standards checks for source size, complexity, mock leakage, tests, and reuse, quality-gated acceleration workflows, smart route guards, project-scoped subagent activation, plugin upgrade migration tools with AGENTS.md/CLAUDE.md rule-template drift detection, opt-in design-system governance assets, DESIGN.md-gated UI workflows with full-service or basic mode, and scheduled-memory examples so future Codex or Claude Code sessions can preserve project rules, conventions, decisions, risks, design constraints, and durable memory while still moving quickly.

## Primary Users

- Codex- or Claude Code-powered maintainers who want strict iterative development rules in a repository.
- Project teams that want version-controlled governance files, memory files, and review workflows.

## Product Surfaces

- Plugin manifest: `.codex-plugin/plugin.json`
- Claude Code plugin manifest: `.claude-plugin/plugin.json`
- Skill catalog: `skills/`
- Claude Code adapter: `claude/`
- Governance templates: `templates/`
- Project-scoped Codex agents and prompts: `.codex/`
- Deterministic helper scripts: `tools/` and `skills/*/scripts/`
- Plugin-owned managed assets: `managed-assets/`
- Harness docs and release notes: `docs/harness/`, `releases/`
- Examples and fixtures: `examples/`
- Self-tests: `tests/selftest.py`

## Non-Goals

- This repository is not an application runtime.
- This repository does not define a web UI, backend service, or HTTP API.
- This repository should not introduce project dependencies unless an explicit decision record approves them.

## Evidence

- `README.md` describes the plugin purpose, skill catalog, install paths, deterministic scripts, and tests.
- `.codex-plugin/plugin.json` declares the plugin identity, version, skills path, MCP config path, and default prompts.
- `.claude-plugin/plugin.json` declares the Claude Code plugin identity, component paths, hooks, agents, commands, skills, and MCP config path.
- `tests/selftest.py` validates manifest shape, skill metadata, required templates, and deterministic helper behavior.
