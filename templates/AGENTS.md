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

When `.project-governor/context/DOCS_MANIFEST.json` and `CONTEXT_INDEX.json` are available, use them first to locate relevant sections. Read line-range `recommended_sections` before opening whole documents; escalate to full required-reading files only when the section results are insufficient, stale, or the change touches public contracts/templates.

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

1. `task-router` to choose route, lane, quality level, change budget, and route guard requirements.
2. `context-pack-builder` to produce a minimal task context pack.
3. `pattern-reuse-engine` to define mandatory reuse and forbidden duplicates.
4. `test-first-synthesizer` for behavior and regression coverage.
5. `parallel-feature-builder` with read-only subagents first, then one bounded implementation writer.
6. `route-guard` after fast-lane implementation, especially for `micro_patch`.
7. `quality-gate` before final response.
8. `repair-loop` only for bounded repairs when the gate fails.
9. `merge-readiness` before PR or merge.

Use `micro_patch` only for explicit local style/copy changes. If actual diff exceeds route guard, stop and reroute. Do not use multiple write agents on overlapping production code. Do not skip quality gates for speed.

## Automatic skill and subagent activation

The user should not need to manually list subagents or pick models after Project Governor initialization.

When a task is non-trivial, the main Codex agent must automatically:

1. Run `task-router` or infer the current route if a route already exists.
2. Run `subagent-activation` when the route or downstream skill has `subagent_mode` of `optional` or `required`.
3. Use project-scoped agents from `.codex/agents/` when present.
4. Use `gpt-5.4-mini` for read-heavy scouting and low-risk support work.
5. Use `gpt-5.4` with medium/high reasoning for implementation, risk review, architecture review, security-sensitive work, and final quality review.
6. Explicitly spawn the selected subagents, wait for all read-only subagents, consolidate their findings, and only then write code.

Do not spawn subagents for `micro_patch` unless route-guard fails, confidence is low, or the target unexpectedly touches a shared/global component.

## Context navigation policy

- Start with `.project-governor/context/DOCS_MANIFEST.json`, `.project-governor/context/SESSION_BRIEF.md`, and `query_context_index.py`.
- Prefer route-specific doc packs and `must_read_sections` line ranges before full documents.
- Exclude docs marked `stale` or `superseded` unless the task explicitly asks for history, cleanup, or migration review.
- Stay within the route context budget; if full documents are needed, record the reason in the task context pack or final evidence.

## Project Governor upgrades

When upgrading Project Governor, use `plugin-upgrade-migrator` behavior. Do not overwrite initialized project governance files blindly. Show new features, inspect `.project-governor/INSTALL_MANIFEST.json`, generate an upgrade plan, apply only safe operations, and leave user-modified files for manual review or three-way merge. Memory files are append-only and decision records must not be overwritten.

When a new Project Governor version adds mandatory rules or workflows to the `AGENTS.md` template, the upgrade plan must surface that `AGENTS.md` template drift. Unmodified installed files may be replaced from the latest template; user-modified files must remain manual review or three-way merge items.

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
- One-off failed commands, error signatures, and corrective lessons go to `.project-governor/state/COMMAND_LEARNINGS.json` so the next session can retrieve them with `context-indexer --memory-search`.
- Stale, superseded, or bloated memory candidates go to `.project-governor/state/MEMORY_HYGIENE.json` until a maintainer marks the source memory as superseded or prunes it.
- Architectural decisions go to `docs/decisions/ADR-*.md`.
- Product decisions go to `docs/decisions/PDR-*.md`.

Every durable memory update must include date, status, source, and evidence.
Do not write speculation as fact.
If confidence is low, record an open question instead.
For non-trivial sessions, run memory search at startup for related prior failures and run `record_session_learning.py` before final response when a command failed, an assumption was corrected, or memory looked stale.

## Subagent usage

For broad audits, PR governance, or existing-project initialization, use read-only subagents for independent review dimensions. Keep the main agent focused on decisions and final patches.

## Verification

Before final response, run the required quality level from `docs/quality/QUALITY_GATE_POLICY.md`, plus relevant tests, lint, typecheck, implementation guard, style drift check, and architecture drift check.
If a command cannot run, explain why and what was verified instead.

## Research policy

Before adopting new capabilities, libraries, governance rules, agent patterns, or plugin features, run `research-radar` in advisory mode.
Before version upgrades, run `version-researcher` before `upgrade-advisor` when release evidence is unclear or multiple versions are available.
Do not implement or upgrade until the user selects a path.
