# Roadmap

## Current Phase

Project Governor Harness v6.2.2 with Claude Code plugin compatibility, initialized self-governance, engineering standards governance, diagnostics-baseline cleanup, token-efficient docs navigation through `DOCS_MANIFEST.json`, architecture-aware roles, section-level context retrieval, route-specific doc packs, session-learning ledgers for failed commands and stale memory, proactive memory-search startup policy, user-level Git install/update support for local marketplaces, advisory research gates, quality-gated acceleration, clean reinstall management, opt-in DESIGN.md governance, DESIGN.md-gated UI workflows, context-index v2, governed memory search, AGENTS.md/CLAUDE.md rule-template drift migration, session lifecycle state, evidence manifests, skill catalog consolidation, compact default prompts, and harness doctor checks.

## Current Maintained Surfaces

- Plugin metadata and public README.
- Claude Code plugin metadata and adapter files.
- Skill documentation under `skills/`.
- Deterministic helper scripts under `tools/` and `skills/*/scripts/`.
- Governance templates under `templates/`.
- Plugin-owned managed assets under `managed-assets/`.
- Harness docs and release notes under `docs/harness/` and `releases/`.
- Example inputs and scheduled-memory examples under `examples/`.
- Self-test workflow under `tests/` and `.github/workflows/selftest.yml`.

## Near-Term Priorities

- Keep self-tests aligned with every new skill, template, and helper script.
- Keep engineering standards thresholds conservative and evidence-backed.
- Keep managed assets clearly separated from target-project templates unless a user explicitly opts in.
- Keep research and release-research policies aligned with the advisory-only upgrade model.
- Fill root governance docs only with facts confirmed from repository evidence.
- Preserve dependency-free Python helper scripts unless an explicit decision approves a new dependency.
- Tighten public CLI contracts when helper scripts change.

## Later Candidates

- Add stronger contract tests for helper-script error behavior.
- Decide whether research registers should gain deterministic validation.
- Clarify thresholds for when a change requires a task iteration plan.
- Decide whether template docs should remain generic or include richer default guidance.

## Evidence

- `.codex-plugin/plugin.json` declares version `6.2.2`.
- `README.md` lists 35+ skills and deterministic script entrypoints.
- `.github/workflows/selftest.yml` runs the repository self-test on push, pull request, and workflow dispatch.
