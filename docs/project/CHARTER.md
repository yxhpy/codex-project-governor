# Project Charter

## Project identity

`codex-project-governor` is a Codex plugin for making repositories self-governing across Codex sessions.

## Purpose

The project provides governance templates, Codex skills, deterministic helper scripts, marketplace examples, user-level Git install/update support for local marketplaces, Harness v6.0.4 task routing, GPT-5.5-aware runtime planning, compact context indexing, governed memory search, session state, evidence manifests, quality-gated acceleration workflows, smart route guards, project-scoped subagent activation, plugin upgrade migration tools with AGENTS.md rule-template drift detection, opt-in design-system governance assets, DESIGN.md-gated UI workflows with full-service or basic mode, and scheduled-memory examples so future Codex sessions can preserve project rules, conventions, decisions, risks, design constraints, and durable memory while still moving quickly.

## Primary Users

- Codex-powered maintainers who want strict iterative development rules in a repository.
- Project teams that want version-controlled governance files, memory files, and review workflows.

## Product Surfaces

- Plugin manifest: `.codex-plugin/plugin.json`
- Skill catalog: `skills/`
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
- `tests/selftest.py` validates manifest shape, skill metadata, required templates, and deterministic helper behavior.
