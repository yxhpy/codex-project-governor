# Project Memory

This file stores durable project facts that should survive conversations, agents, and contributors.

Do not write:

- temporary guesses
- raw brainstorming
- unresolved opinions
- secrets
- stale roadmap assumptions
- facts without evidence

## Current product truth

| Field | Value | Evidence | Status |
|---|---|---|---|
| Product | `codex-project-governor`, a Codex governance plugin | `README.md`, `.codex-plugin/plugin.json` | confirmed |
| Primary user | Codex-powered maintainers and project teams that want repository-scoped governance | `README.md`, `skills/init-existing-project/SKILL.md`, `skills/pr-governance-review/SKILL.md` | inferred from evidence |
| Current phase | v0.2.0 plugin with upgrade-advisor and self-tests | `.codex-plugin/plugin.json`, `README.md`, `tests/selftest.py` | confirmed |
| Success metric | Self-tests pass and initialized repositories receive governance templates without application-code changes | `README.md`, `tests/selftest.py`, `tools/init_project.py` | confirmed |

## Durable facts

| Date | Fact | Source | Status | Evidence |
|---|---|---|---|---|
| 2026-04-21 | The repository is organized around plugin metadata, skills, templates, deterministic scripts, examples, and self-tests. | init-existing-project analysis | confirmed | `.codex-plugin/plugin.json`, `README.md`, `tests/selftest.py` |
| 2026-04-21 | The project ships 11 bundled skills in `skills/`. | init-existing-project analysis | confirmed | `README.md`, `tests/selftest.py` |
| 2026-04-21 | The initializer copies files from `templates/` and preserves existing files unless overwrite is requested. | init-existing-project analysis | confirmed | `tools/init_project.py` |
| 2026-04-21 | The repository has no application runtime, HTTP service, or local UI component implementation. | init-existing-project analysis | confirmed | `.mcp.json`, `README.md`, `assets/icon.png`, file tree |

## Durable decisions summary

| Date | Decision | Decision record | Status |
|---|---|---|---|

## Product constraints

| Date | Constraint | Source | Status | Evidence |
|---|---|---|---|---|
| 2026-04-21 | Work should preserve plugin, skill, template, script, example, and self-test boundaries. | init-existing-project analysis | confirmed | `AGENTS.md`, `docs/architecture/ARCHITECTURE.md` |
| 2026-04-21 | Durable memory must be evidence-backed and should not store speculation or secrets. | init-existing-project analysis | confirmed | `AGENTS.md`, `docs/memory/PROJECT_MEMORY.md` |

## Technical constraints

| Date | Constraint | Source | Status | Evidence |
|---|---|---|---|---|
| 2026-04-21 | Deterministic scripts should remain Python standard-library CLIs unless a decision record approves a dependency. | init-existing-project analysis | confirmed | `tools/init_project.py`, `skills/*/scripts/*.py`, `.github/workflows/selftest.yml` |
| 2026-04-21 | Template path changes are public behavior changes because templates are copied into downstream repositories. | init-existing-project analysis | confirmed | `tools/init_project.py`, `templates/`, `tests/selftest.py` |
| 2026-04-21 | Helper script JSON output shapes are public contracts and should be covered by tests. | init-existing-project analysis | confirmed | `docs/architecture/API_CONTRACTS.md`, `tests/selftest.py` |

## Repeated agent mistakes summary

See `REPEATED_AGENT_MISTAKES.md`.

## Last reviewed

- Date: 2026-04-21
- Reviewer: Codex init-existing-project workflow
