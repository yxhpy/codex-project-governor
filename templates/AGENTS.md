# AGENTS.md

## Project operating mode

This repository is governed by Project Governor.
Codex must work as an iterative maintainer, not as a greenfield developer.

## Required reading before non-trivial changes

1. `docs/project/CHARTER.md`
2. `docs/conventions/CONVENTION_MANIFEST.md`
3. `docs/conventions/ITERATION_CONTRACT.md`
4. `docs/conventions/PATTERN_REGISTRY.md`
5. `docs/conventions/COMPONENT_REGISTRY.md`
6. `docs/architecture/ARCHITECTURE.md`
7. Relevant nested `AGENTS.md` files
8. Adjacent existing code

## Iteration-first rule

Before implementation:

- inspect existing adjacent code
- identify reusable patterns
- create or update `tasks/<date>-<slug>/ITERATION_PLAN.md`
- avoid new files unless justified in the iteration plan
- avoid new dependencies unless approved in a decision record
- preserve API, UI, data, and architecture conventions
- choose the smallest coherent patch over a rewrite

## Forbidden by default

Do not:

- rewrite modules from scratch
- create duplicate components
- introduce new styling systems
- introduce new state management patterns
- introduce new API response shapes
- introduce new directory conventions
- add dependencies without a dependency decision
- silently change user-facing behavior
- modify durable memory without evidence
- delete decision history
- store secrets in code, docs, logs, or memory files

## Upgrade policy

Before upgrading dependencies, frameworks, tools, SDKs, runtimes, or Project Governor assets, run `upgrade-advisor` in advisory mode. Do not edit manifests or install packages until the user selects an upgrade path. Follow `docs/upgrades/UPGRADE_POLICY.md` and record decisions in `docs/upgrades/UPGRADE_REGISTER.md`.

## Quality-gated acceleration

For coding work where speed matters, use the acceleration pipeline instead of ad hoc implementation:

1. `task-router` to choose route, lane, quality level, and change budget.
2. `context-pack-builder` to produce a minimal task context pack.
3. `pattern-reuse-engine` to define mandatory reuse and forbidden duplicates.
4. `test-first-synthesizer` for behavior and regression coverage.
5. `parallel-feature-builder` with read-only subagents first, then one bounded implementation writer.
6. `quality-gate` before final response.
7. `repair-loop` only for bounded repairs when the gate fails.
8. `merge-readiness` before PR or merge.

Do not use multiple write agents on overlapping production code. Do not skip quality gates for speed.

## Documentation updates

Update docs when changing:

- product behavior
- API contracts
- data model
- architecture
- design system
- repeated agent mistakes
- project constraints
- risks or known limitations

## Memory policy

- Durable facts go to `docs/memory/PROJECT_MEMORY.md`.
- Unresolved questions go to `docs/memory/OPEN_QUESTIONS.md`.
- Repeated agent mistakes go to `docs/memory/REPEATED_AGENT_MISTAKES.md`.
- Risks go to `docs/memory/RISK_REGISTER.md`.
- Architectural decisions go to `docs/decisions/ADR-*.md`.
- Product decisions go to `docs/decisions/PDR-*.md`.

Every durable memory update must include date, status, source, and evidence.
Do not write speculation as fact.
If confidence is low, record an open question instead.

## Subagent usage

For broad audits, PR governance, or existing-project initialization, use read-only subagents for independent review dimensions. Keep the main agent focused on decisions and final patches.

## Verification

Before final response, run the required quality level from `docs/quality/QUALITY_GATE_POLICY.md`, plus relevant tests, lint, typecheck, implementation guard, style drift check, and architecture drift check.
If a command cannot run, explain why and what was verified instead.

## Research policy

Before adopting new capabilities, libraries, governance rules, agent patterns, or plugin features, run `research-radar` in advisory mode.
Before version upgrades, run `version-researcher` before `upgrade-advisor` when release evidence is unclear or multiple versions are available.
Do not implement or upgrade until the user selects a path.
