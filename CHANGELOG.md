# Changelog

## 6.2.3 - Slot-Based Governance Artifacts

### Added

- Added deterministic governance artifact rendering from structured `*.slots.json` files, starting with `ITERATION_PLAN.md`.
- Added revision-checked generated artifact update patches so plans can change during execution without rewriting fixed Markdown templates.
- Added machine-readable artifact template metadata and a slot schema for `iteration_plan_v1`.

### Changed

- Updated `iteration-planner`, `AGENTS.md`, and iteration contracts to prefer slot files plus deterministic render/update scripts for generated governance artifacts.
- Updated context indexing so generated Markdown with a `generated_from` marker is indexed from its source slots when available, reducing read-side template noise.

### Compatibility

- Existing CLI entry points, skill names, and initialized-project behavior remain compatible.
- No new third-party dependencies.
- Existing generated Markdown still indexes normally when a source slot file is missing.

## 6.2.2 - Diagnostics Baseline Cleanup

### Added

- Added split helper modules for context-index roles, task-router policy/config, DESIGN.md service HTTP calls, and self-test helpers.

### Changed

- Refactored diagnostics-heavy helper scripts and tests so engineering standards pass with a clean all-scope baseline.
- Updated context role classification so `docs/architecture/**` is indexed as architecture context.
- Updated DESIGN.md service smoke identity to derive its version from plugin metadata.

### Compatibility

- Existing CLI entry points, output schemas, skill names, and template paths remain compatible.
- No initialized-project migration is required.

## 6.2.0 - Claude Code Compatibility Adapter

### Added

- Added Claude Code plugin metadata, `pg-*` commands, Claude subagents, plugin hooks, and marketplace metadata.
- Added `templates/CLAUDE.md` so initialized projects can expose Claude Code project memory while importing shared `AGENTS.md` rules.
- Added `docs/compat/CLAUDE_CODE.md` with component mapping and validation guidance.

### Changed

- `tools/init_project.py` now copies `CLAUDE.md` in the clean profile.
- `templates/AGENTS.md` now uses cross-agent wording where Claude Code imports the same rules.
- Public docs now describe Codex and Claude Code plugin surfaces.

### Compatibility

- Existing Codex plugin behavior remains unchanged.
- No new third-party dependencies.
- Claude adapter validation is covered by self-tests and `claude plugin validate .`.

## 6.1.0 - Engineering Standards Governance

### Added

- Added `engineering-standards-governor` with a dependency-free scanner for source file size, function length, approximate function complexity, production mock imports, mock-like production identifiers, mock inventory, and test files without assertion markers.
- Added engineering standards policy templates for backend/frontend maintainability, reuse-first coding, mock governance, and test matrix expectations.
- Added `ENGINEERING_STANDARDS_REPORT.md` and expanded `TEST_PLAN.md` / `QUALITY_REPORT.md` templates.

### Changed

- `task-router` now includes `engineering-standards-governor` in coding workflows before `quality-gate`.
- `quality-gate` can consume an `engineering_standards` result and fail on blockers; strict gates treat unresolved engineering warnings as blockers.
- `pattern-reuse-engine` now classifies fixture/mock/testdata candidates as `test_double` reuse candidates.

### Compatibility

- No new third-party dependencies.
- The new scanner output schema is additive and documented in `docs/architecture/API_CONTRACTS.md`.
- Existing initialized projects can receive the new policy, prompt, and task templates through `plugin-upgrade-migrator`; user-modified files remain manual review or three-way merge items.

## 6.0.6 - Token-Efficient Docs Navigation

### Added

- Added generated `.project-governor/context/DOCS_MANIFEST.json` so agents can inspect a compact documentation map before opening large docs.
- Added section-level Markdown indexing and `recommended_sections` / `must_read_sections` query output with line ranges.
- Added route-specific doc packs from `task-router` and surfaced them in `gpt55-auto-orchestrator` runtime plans.
- Added context-pack token budgets, compression policy, progressive read plans, and stale/superseded doc avoid lists.

### Changed

- Updated context policies so agents prefer docs manifest, session brief, memory search, and section ranges before full documents.
- Updated `AGENTS.md` templates so initialized projects can receive the new context navigation workflow through upgrade planning.

### Fixed

- Fixed DESIGN.md basic mode for Codex hooks and Windows sessions by honoring `DESIGN_BASIC_MODE=1` from project-root `.env-design`, not only inherited shell environment variables.

### Compatibility

- No new third-party dependencies.
- Existing context-index JSON fields remain additive; consumers can ignore the new docs manifest, section, route doc pack, and token-budget fields.

## 6.0.5 - Session Learning Memory Loop

### Added

- Added `.project-governor/state/COMMAND_LEARNINGS.json` for one-off failed commands, error signatures, and corrective lessons that should be retrievable in future sessions.
- Added `.project-governor/state/MEMORY_HYGIENE.json` for stale, superseded, or bloated memory candidates that need review before pruning or marking superseded.
- Added `skills/memory-compact/scripts/record_session_learning.py` to classify and write session learnings across command-learning, repeated-mistake, stale-memory, open-question, and risk layers.
- Added runtime-plan policy requiring non-trivial sessions to run memory search at startup and record session learnings before final response when commands fail or memory goes stale.

### Changed

- Updated `AGENTS.md`, `templates/AGENTS.md`, session lifecycle, context-index session briefs, and user docs so memory search and learning capture are proactive workflow steps instead of optional reminders.

### Compatibility

- No new third-party dependencies.
- Existing memory-search behavior remains read-only unless `record_session_learning.py --apply` is used.
- Existing initialized projects can receive the new state files through `plugin-upgrade-migrator`; user-modified `AGENTS.md` files remain manual review or three-way merge items.

## 6.0.4 - Local Marketplace Git Update Path

### Added

- Added `tools/install_or_update_user_plugin.py` to install or update the user-level Project Governor Git checkout and ensure the local marketplace entry exists.
- Added tests for dry-run planning, local Git clone/update behavior, marketplace entry writing, and dirty checkout protection.

### Changed

- Updated install and upgrade docs to clarify that `source: local` marketplace entries are local pointers and are not fetched by built-in Git marketplace upgrade commands.

### Compatibility

- No new third-party dependencies.
- Marketplace entry shape remains `source: local`.
- Existing initialized project migration flows remain unchanged; use `plugin-upgrade-migrator` after the plugin checkout itself is updated.

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
