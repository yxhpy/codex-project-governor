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
| Current phase | v0.5.0 plugin with GPT-5.5 auto orchestration, context indexing, DESIGN.md governance, clean reinstall management, project hygiene self-inspection fix, clean initialization, plugin upgrade migration, routing, quality gates, and self-tests | `.codex-plugin/plugin.json`, `README.zh-CN.md`, `tests/selftest.py` | confirmed |
| Success metric | Self-tests pass and initialized repositories receive governance templates without application-code changes | `README.md`, `tests/selftest.py`, `tools/init_project.py` | confirmed |

## Durable facts

| Date | Fact | Source | Status | Evidence |
|---|---|---|---|---|
| 2026-04-21 | The repository is organized around plugin metadata, skills, templates, deterministic scripts, examples, and self-tests. | init-existing-project analysis | confirmed | `.codex-plugin/plugin.json`, `README.md`, `tests/selftest.py` |
| 2026-04-24 | The project ships 30 bundled skills in `skills/`. | v0.5.0 release workflow | confirmed | `README.md`, `tests/selftest.py`, `skills/gpt55-auto-orchestrator/SKILL.md`, `skills/context-indexer/SKILL.md` |
| 2026-04-22 | The initializer copies project-owned governance files from `templates/` by default, preserves existing files unless overwrite is requested, and exposes `--profile legacy-full` for bundled `.codex` runtime assets. | v0.4.4 release merge | confirmed | `tools/init_project.py`, `docs/architecture/API_CONTRACTS.md` |
| 2026-04-21 | The repository has no application runtime, HTTP service, or local UI component implementation. | init-existing-project analysis | confirmed | `.mcp.json`, `README.md`, `assets/icon.png`, file tree |
| 2026-04-22 | v0.4.4 introduces clean initialization by default and a `project-hygiene-doctor` workflow for diagnosing plugin-global assets in target projects. | v0.4.4 release merge | confirmed | `CHANGELOG.md`, `tools/init_project.py`, `skills/project-hygiene-doctor/SKILL.md`, `releases/0.4.4.md` |
| 2026-04-22 | v0.4.5 fixes `project-hygiene-doctor` self-inspection so this plugin source repository can keep its own root `.codex` runtime assets while downstream copied plugin-source leaks still require manual review. | v0.4.5 release workflow | confirmed | `CHANGELOG.md`, `skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py`, `tests/test_project_hygiene_doctor.py`, `releases/0.4.5.md` |
| 2026-04-22 | v0.4.6 adds `clean-reinstall-manager` for user-level reinstall instructions, governed-project discovery, clean project refresh, and plugin-global noise quarantine without overwriting memory or decisions. | v0.4.6 release workflow | confirmed | `CHANGELOG.md`, `skills/clean-reinstall-manager/SKILL.md`, `tests/test_clean_reinstall_manager.py`, `releases/0.4.6.md` |
| 2026-04-23 | v0.4.7 adds `design-md-governor` with opt-in DESIGN.md governance, plugin-owned managed assets, and dependency-free lint, summarize, and diff helpers. | v0.4.7 drop-in merge | confirmed | `CHANGELOG.md`, `skills/design-md-governor/SKILL.md`, `managed-assets/design-md/DESIGN_MD_POLICY.md`, `tests/test_design_md_governor.py`, `releases/0.4.7.md` |
| 2026-04-24 | v0.5.0 adds GPT-5.5 auto orchestration, context indexing, project-owned runtime mode, and clean reinstall latest-runtime application without copying plugin-global assets into target projects. | v0.5.0 Downloads patch merge | confirmed | `CHANGELOG.md`, `skills/gpt55-auto-orchestrator/SKILL.md`, `skills/context-indexer/SKILL.md`, `templates/.project-governor/runtime/GPT55_RUNTIME_MODE.json`, `tests/test_gpt55_auto_orchestration.py`, `releases/0.5.0.md` |

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

- Date: 2026-04-24
- Reviewer: Codex v0.5.0 GPT-5.5 Auto Orchestration workflow
