# Architecture

## Overview

This repository is a Codex plugin and governance-template bundle. It has no service backend, frontend app, database, or long-running runtime.

## Layers

1. Plugin metadata
   - `.codex-plugin/plugin.json`
   - `.mcp.json`
2. Project-scoped Codex configuration
   - `.codex/config.toml`
   - `.codex/agents/*.toml`
   - `.codex/prompts/*.md`
   - `.codex/rules/project.rules`
   - `.codex/hooks/**`
3. Skill workflows
   - `skills/<skill>/SKILL.md`
   - Optional deterministic scripts under `skills/<skill>/scripts/`
4. Template payload
   - `templates/AGENTS.md`
   - `templates/docs/**`
   - `templates/.codex/**`
   - `templates/tasks/_template/**`
5. Plugin-owned managed assets
   - `managed-assets/design-md/**`
6. Initializer and compatibility tools
   - `tools/init_project.py`
   - `tools/init_existing_project.py`
7. Examples and fixtures
   - `examples/*.json`
   - `examples/cron/**`
   - `examples/launchd/**`
   - `examples/github-actions/**`
8. Validation
   - `tests/selftest.py`
   - `.github/workflows/selftest.yml`

## Dependency Direction

- Tests may call tools and skill scripts.
- Tools may read from `templates/`.
- Skill scripts should remain standalone and should not depend on each other unless explicitly documented.
- Templates should not depend on generated output under `reports/`.
- Managed assets are plugin-owned source material. They are not target-project files unless a user explicitly opts in and creates project-owned copies.

## Generated Output

- `tools/init_project.py` writes `reports/project-governor/init-report.json` in the target repository.
- `reports/` is ignored by `.gitignore`.

## Known Coupling Risks

- `tools/init_existing_project.py` is a compatibility wrapper that mutates `sys.path` and ignores its `plugin_root` argument.
- `tools/init_project.py` uses hard-coded `APP_PREFIXES` and `PACKAGE_FILES` heuristics to avoid copying application paths.

## Evidence

- `.codex-plugin/plugin.json`
- `.mcp.json`
- `README.md`
- `tools/init_project.py`
- `tools/init_existing_project.py`
- `tests/selftest.py`
