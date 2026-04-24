# Changelog

## 0.5.0 - GPT-5.5 Auto Orchestration

### Added

- Added `gpt55-auto-orchestrator` skill for automatic workflow, model, subagent, context-budget, and quality-gate selection.
- Added `context-indexer` skill plus deterministic context index build/query helpers.
- Added project-owned GPT-5.5 runtime mode template under `.project-governor/runtime/`.
- Added clean reinstall helper support for applying latest runtime mode to current or discovered governed projects.

### Compatibility

- No new third-party dependencies.
- Project runtime mode and context files are project-owned `.project-governor/` state.
- Plugin-global `.codex` agents, prompts, and config remain outside clean target-project initialization unless legacy-full is explicitly requested.

## 0.4.7 - DESIGN.md Governor

### Added

- Added `design-md-governor` skill for opt-in project `DESIGN.md` governance.
- Added deterministic DESIGN.md lint, summarize, and diff helpers.
- Added plugin-owned `managed-assets/design-md/` template and policy files, examples, release metadata, and tests.

### Compatibility

- No new third-party dependencies.
- No target-project migration is required; project `DESIGN.md` creation remains explicit opt-in behavior.

## 0.4.6 - Clean Reinstall Manager

### Added

- Added `clean-reinstall-manager` skill for user-level plugin reinstall planning, governed-project discovery, and safe initialized-project refresh.
- Added deterministic helpers for reinstall instruction generation, governed project discovery, refresh planning, and orchestrated clean reinstall workflows.
- Added `CLEAN_REINSTALL_POLICY.md`, a clean reinstall prompt template, release metadata, and tests for the new workflow.

### Fixed

- The clean refresh helper stops when the requested project path is the Project Governor plugin root, avoiding accidental quarantine of plugin-owned `skills/`, `templates/`, or `releases/` assets.

## 0.4.5 — Hygiene Self-Inspection Fix

### Fixed

- Fixed `project-hygiene-doctor` self-inspection for the Project Governor plugin repository: when `--project` matches `--plugin-root`, the repository's own `.codex/agents`, `.codex/prompts`, and `.codex/config.toml` are classified as plugin repository runtime assets instead of target-project cleanup findings.
- Tightened plugin repository detection so a downstream target project that accidentally contains copied `.codex-plugin` or `skills` files is still flagged for manual review when it is not the configured plugin root.

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
