# Changelog

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
