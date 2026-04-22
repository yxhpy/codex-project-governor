# AGENTS.md

## Project Operating Mode

This repository is `codex-project-governor`, a Codex plugin and governance-template bundle. Work as an iterative maintainer. Do not treat it as an application repo or a greenfield framework.

## Required Reading

Before non-trivial changes, read:

1. `docs/project/CHARTER.md`
2. `docs/conventions/CONVENTION_MANIFEST.md`
3. `docs/conventions/ITERATION_CONTRACT.md`
4. `docs/architecture/ARCHITECTURE.md`
5. `README.md`
6. `.codex-plugin/plugin.json`
7. Adjacent files under `skills/`, `templates/`, `tools/`, `tests/`, or `examples/`

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
- Architectural decisions go to `docs/decisions/ADR-*.md`.
- Product decisions go to `docs/decisions/PDR-*.md`.

Every durable memory update must include date, status, source, and evidence. If confidence is low, record an open question instead.

## Verification

Run the narrowest relevant checks:

- Full self-test: `python3 tests/selftest.py`
- Make wrapper: `make test`
- Python syntax for edited scripts: `python3 -m compileall tools skills tests`
- Init smoke test when templates or initializer behavior changed: `python3 tools/init_project.py --mode existing --target <tmpdir> --json`

If a check cannot run, state why and report the closest verified substitute.
