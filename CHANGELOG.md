# Changelog

## 6.0.3 - AGENTS Rule Template Drift Migration

### Added

- Added automatic `AGENTS.md` rule-template drift detection to `plugin-upgrade-migrator`.
- Added `review_rule_template_drift` planning so already initialized projects can see mandatory rules added to the latest `templates/AGENTS.md`.
- Added regression tests for unchanged installed `AGENTS.md` safe updates and user-modified `AGENTS.md` manual review.

### Compatibility

- No new third-party dependencies.
- User-modified `AGENTS.md` files are not overwritten; they remain manual review or three-way merge items.
- Existing migration JSON output remains additive.

## 6.0.2 - Governed Memory Search

### Added

- Added `context-indexer --memory-search --auto-build` for governed project memory/history lookup without raw chat transcript scanning or complex shell pipelines.
- Added memory-search text output for quick human-readable lookup results.
- Added `task_history` and `governance_history` context roles so task plans, project state, release notes, research docs, and upgrade docs can be retrieved as history.

### Compatibility

- No new third-party dependencies.
- Existing context-index JSON output remains additive; default context queries keep their prior behavior.

## 6.0.1 - DESIGN.md Aesthetic Governor

### Added

- Added `design-md-aesthetic-governor` for UI/frontend review, prototyping, and implementation gates.
- Added full-service design workflow: GPT/Codex orchestrates, Stitch MCP supports visual prototype exploration, and Gemini reviews design quality against `DESIGN.md`.
- Added `DESIGN_BASIC_MODE=1` so users can intentionally do frontend work without Gemini/Stitch setup while retaining local DESIGN.md checks.
- Added `.env-design` support for project-local Gemini/Stitch configuration without committing secrets.
- Added remote Stitch MCP configuration at `https://stitch.googleapis.com/mcp` and real-service smoke checks for Gemini-compatible chat completions plus Stitch MCP initialization.
- Added explicit `GEMINI_PROTOCOL=auto|openai|gemini` support and `design_service_review.py` to record repeatable Gemini/Stitch full-service design review evidence.
- Added native Gemini gateway-root guidance and HTML-response hints so gateways that expose `/gemini/v1beta` can be configured correctly.
- Added Codex hooks for UI prompt reminders and UI edit preflight checks.

### Compatibility

- No new third-party Python dependencies.
- `.env-design` is ignored by the plugin repository and target projects can add it to `.git/info/exclude`.

## 6.0.0 - Project Governor Harness v6.0

### Added

- Added Harness v6 docs, runtime policy, release notes, and plugin manifest positioning.
- Added `session-lifecycle` state management under `.project-governor/state`.
- Added `evidence-manifest` templates and helper script under `.project-governor/evidence/<task-id>/`.
- Added `harness-doctor` for install shape, context freshness, state, and execution readiness checks.
- Added context-index schema v2 with git metadata, mtime, language, symbols, imports, headings, stale hints, and secret redaction.
- Added git-derived route guard fact collection.

### Changed

- `task-router` is now the Harness v6 route source of truth.
- `gpt55-auto-orchestrator` now wraps router classification and performs runtime planning.
- Standard and risky feature routes include test-first planning and evidence-aware gates.
- `quality-gate` and `merge-readiness` now understand evidence manifests.

### Compatibility

- No new third-party dependencies.
- Existing skills and historical release metadata are preserved.
- Target projects should refresh copied governance templates before relying on Harness v6 state and evidence files.

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
