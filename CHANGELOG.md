# Changelog

## 0.4.4 — Project Hygiene Doctor

### Added

- Added `project-hygiene-doctor` skill to detect and quarantine plugin-global assets that should not live in initialized target projects.
- Added clean init profile in `tools/init_project.py`; target projects now receive project-owned governance files only by default.
- Added `PROJECT_HYGIENE_POLICY.md` and hygiene prompt template.

### Changed

- Default initialization skips `.codex/agents`, `.codex/prompts`, and `.codex/config.toml`; these remain plugin-owned unless the user opts into `--profile legacy-full`.

## 0.4.3 — Plugin Upgrade Migrator

### Added

- `plugin-upgrade-migrator` skill.
- `releases/FEATURE_MATRIX.json` for new-feature discovery.
- `releases/MIGRATIONS.json` for project-file migration planning.
- `.project-governor/INSTALL_MANIFEST.json` template.
- Safe migration helpers for inspect, compare, plan, and safe apply.

### Migration

Use `plugin-upgrade-migrator` to show what is new, plan a safe migration, and avoid overwriting project customizations.

## 0.4.2 — Explicit Subagent Activation

Adds workflow orchestration, subagent activation, model routing, and project-scoped `.codex/agents/*.toml` templates.

## 0.4.1 — Smart Routing Guard

Adds `micro_patch`, negative constraints, `route-guard`, and quality-gate route validation.
