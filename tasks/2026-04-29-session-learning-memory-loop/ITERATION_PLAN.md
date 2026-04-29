# Iteration Plan: Session Learning Memory Loop

## User request

Fix Project Governor's memory behavior so new sessions do not repeat known failed commands, do not depend on the user saying "remember this", classify memories into the right layer, use memory search proactively, and manage stale memory instead of letting memory grow forever.

## Existing behavior

`context-indexer --memory-search` can query governed memory/history files, but runtime planning does not require it at session start. `memory-compact` can classify candidate text, but no deterministic helper writes one-off command failures, repeated mistakes, or stale-memory candidates into project-owned retrievable state. Session lifecycle initializes state and progress, but not a command-learning or memory-hygiene ledger.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
|---|---|---|
| Project-owned state under `.project-governor/state/` | `skills/session-lifecycle/scripts/session_lifecycle.py`, `templates/.project-governor/state/` | Add command-learning and memory-hygiene ledgers that are indexed by memory search. |
| Memory classification | `skills/memory-compact/scripts/classify_memory_items.py` | Extend classification with command learning and add a writer for session learnings. |
| Memory search | `skills/context-indexer/scripts/query_context_index.py` | Ensure the new state ledgers are retrievable through existing `--memory-search`. |
| Runtime plan policy fields | `skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py` | Add explicit startup memory-search and session-learning requirements. |
| Template drift handling | `templates/AGENTS.md`, `skills/plugin-upgrade-migrator/scripts/plan_migration.py` | Put mandatory memory rules in `templates/AGENTS.md`; existing AGENTS drift detection will surface them. |

## Files expected to change

- `.codex-plugin/plugin.json`
- `AGENTS.md`
- `templates/AGENTS.md`
- `templates/.project-governor/state/COMMAND_LEARNINGS.json`
- `templates/.project-governor/state/MEMORY_HYGIENE.json`
- `skills/memory-compact/SKILL.md`
- `skills/memory-compact/scripts/classify_memory_items.py`
- `skills/memory-compact/scripts/record_session_learning.py`
- `skills/session-lifecycle/SKILL.md`
- `skills/session-lifecycle/scripts/session_lifecycle.py`
- `skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py`
- `skills/context-indexer/scripts/build_context_index.py`
- `tests/test_session_learning.py`
- `tests/test_harness_v6.py`
- `tests/selftest.py`
- `README.md`
- `README.zh-CN.md`
- `docs/zh-CN/USAGE.md`
- `docs/architecture/API_CONTRACTS.md`
- `docs/architecture/DATA_MODEL.md`
- `docs/memory/PROJECT_MEMORY.md`
- `docs/memory/RISK_REGISTER.md`
- `docs/upgrades/UPGRADE_REGISTER.md`
- `releases/FEATURE_MATRIX.json`
- `releases/MIGRATIONS.json`
- `releases/6.0.5.md`

## Files not to change

- Application code outside governance/plugin surfaces
- Dependency manifests or lockfiles
- Existing context-index JSON schema for current entries, except additive policy fields in runtime plan output
- Existing initialized project memory files outside explicit ledger/template updates

## New files

| File | Why existing files cannot cover it |
|---|---|
| `templates/.project-governor/state/COMMAND_LEARNINGS.json` | One-off failed commands need project-owned searchable state before they become repeated mistakes. |
| `templates/.project-governor/state/MEMORY_HYGIENE.json` | Stale or bloated memory needs a review queue separate from durable facts. |
| `skills/memory-compact/scripts/record_session_learning.py` | Classification alone does not write session learnings to the correct memory layer. |
| `tests/test_session_learning.py` | The new layered write behavior and memory-search retrieval need regression coverage. |
| `releases/6.0.5.md` | Versioned release notes are required for the new patch release. |

## Dependencies

No new dependencies. All helper code stays Python standard-library only.

## Tests

- `python3 tests/test_session_learning.py`
- `python3 tests/test_harness_v6.py`
- `python3 tests/test_gpt55_auto_orchestration.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`
- `make test`

## Risks

- Recording command failures could accidentally store secrets. The recorder must detect secret-like values and skip raw storage.
- Repeated mistakes could flood durable memory. One-off items stay in state; repeated items are promoted only when repeat signals are present.
- Stale-memory cleanup could remove useful history. The first step is a hygiene queue; maintainers still mark source memory as superseded or prune deliberately.

## Rollback

Remove the new state templates, recorder script, runtime policy fields, release metadata, and tests. Existing memory search and memory compact behavior remain available but less proactive.
