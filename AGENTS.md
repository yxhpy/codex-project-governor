# AGENTS.md

## Project Operating Mode

This repository is `codex-project-governor`, a Codex and Claude Code plugin/governance-template bundle. Work as an iterative maintainer. Do not treat it as an application repo or a greenfield framework.

## Required Reading

Before non-trivial changes, read:

1. `docs/project/CHARTER.md`
2. `docs/conventions/CONVENTION_MANIFEST.md`
3. `docs/conventions/ITERATION_CONTRACT.md`
4. `docs/architecture/ARCHITECTURE.md`
5. `README.md`
6. `.codex-plugin/plugin.json`
7. Adjacent files under `skills/`, `templates/`, `tools/`, `tests/`, or `examples/`

When `.project-governor/context/DOCS_MANIFEST.json` and `CONTEXT_INDEX.json` are available, use them first to locate relevant sections. Read line-range `recommended_sections` before opening whole documents; escalate to full required-reading files only when the section results are insufficient, stale, or the change touches public contracts/templates.

## Repository Boundaries

- Plugin metadata lives in `.codex-plugin/plugin.json`.
- Skill workflows live under `skills/<skill>/SKILL.md`.
- Deterministic helper scripts live under `tools/` and `skills/*/scripts/`.
- Governance payloads copied into target repositories live under `templates/`.
- Example inputs and marketplace snippets live under `examples/`.
- Self-tests live in `tests/selftest.py`.

## Iteration Rules

- Prefer narrow patches that preserve existing plugin, template, and script boundaries.
- Create or update `tasks/<date>-<slug>/ITERATION_PLAN.md` for non-trivial implementation.
- Keep deterministic scripts dependency-free unless a decision record approves otherwise.
- Preserve CLI JSON output shapes unless an API contract update explains the change.
- Preserve template paths because `tools/init_project.py` copies them into target repositories.
- Do not rewrite a skill, script, or template family when a focused edit is enough.

## Engineering Standards

For coding work that changes production or test code:

- run `engineering-standards-governor` before final `quality-gate`
- keep source files and functions within documented project thresholds unless an ADR/PDR approves a temporary exception
- scan for mock leakage so production code does not import mocks, fixtures, test data, or test-only libraries
- require `TEST_PLAN.md` to cover normal, boundary, error, regression, integration/contract, frontend interaction, and explicit not-tested rationale rows when relevant
- require a `PATTERN_REUSE_PLAN.md` before creating new components, services, hooks, schemas, fixtures, or helpers

Do not leave partial mock implementations in production paths. If a mock is used for an external dependency, record the real contract and the integration, contract, or smoke test that protects it.

## Forbidden By Default

Do not:

- modify application code outside governance surfaces during initialization
- add package manifests, lockfiles, or dependencies without a decision record
- introduce a new runtime, framework, or service layer without an ADR
- change `.codex-plugin/plugin.json` public fields without updating README and tests when needed
- alter deterministic helper output schemas without updating `docs/architecture/API_CONTRACTS.md` and `tests/selftest.py`
- write speculative facts into project memory
- store secrets in code, docs, logs, reports, or memory files

## Upgrade Policy

Before upgrading dependencies, tools, SDKs, runtimes, plugin versions, or governance assets, run `upgrade-advisor` in advisory mode. Do not edit manifests or install packages until the user selects an upgrade path. Record decisions in `docs/upgrades/UPGRADE_REGISTER.md`.

When adding mandatory rules or workflows to `templates/AGENTS.md`, ensure initialized projects will see them during Project Governor upgrades. Update `plugin-upgrade-migrator` planning, migration metadata, or tests so `AGENTS.md` template drift is surfaced without blindly overwriting user-modified project rules.

## Documentation Updates

Update governance docs when changing:

- plugin capabilities or public positioning
- skill workflows
- deterministic CLI contracts
- template output paths or copied file sets
- test expectations
- repeated agent mistakes, risks, or known limitations

## Memory Policy

- Durable facts go to `docs/memory/PROJECT_MEMORY.md`.
- Unresolved questions go to `docs/memory/OPEN_QUESTIONS.md`.
- Repeated agent hazards go to `docs/memory/REPEATED_AGENT_MISTAKES.md`.
- Risks go to `docs/memory/RISK_REGISTER.md`.
- One-off failed commands, error signatures, and corrective lessons go to `.project-governor/state/COMMAND_LEARNINGS.json` so the next session can retrieve them with `context-indexer --memory-search`.
- Stale, superseded, or bloated memory candidates go to `.project-governor/state/MEMORY_HYGIENE.json` until a maintainer marks the source memory as superseded or prunes it.
- Architectural decisions go to `docs/decisions/ADR-*.md`.
- Product decisions go to `docs/decisions/PDR-*.md`.

Every durable memory update must include date, status, source, and evidence. If confidence is low, record an open question instead.
For non-trivial sessions, run memory search at startup for related prior failures and run `record_session_learning.py` before final response when a command failed, an assumption was corrected, or memory looked stale.

## Context Navigation Policy

- Start with `.project-governor/context/DOCS_MANIFEST.json`, `.project-governor/context/SESSION_BRIEF.md`, and `query_context_index.py`.
- Prefer route-specific doc packs and `must_read_sections` line ranges before full documents.
- Exclude docs marked `stale` or `superseded` unless the task explicitly asks for history, cleanup, or migration review.
- Stay within the route context budget; if full documents are needed, record the reason in the task context pack or final evidence.

## Verification

Run the narrowest relevant checks:

- Full self-test: `python3 tests/selftest.py`
- Make wrapper: `make test`
- Python syntax for edited scripts: `python3 -m compileall tools skills tests`
- Init smoke test when templates or initializer behavior changed: `python3 tools/init_project.py --mode existing --target <tmpdir> --json`

If a check cannot run, state why and report the closest verified substitute.
