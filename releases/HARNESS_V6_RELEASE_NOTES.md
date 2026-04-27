# 6.0.0 — Project Governor Harness v6.0

## Added

- Harness v6 runtime contract.
- `session-lifecycle` skill.
- `evidence-manifest` skill.
- `harness-doctor` skill.
- Context index schema v2 with git metadata, mtime, language, symbols, imports, headings, sensitive-file detection, and redaction.
- Git-derived route guard fact collection.
- Evidence-aware quality gate and merge readiness.
- State templates under `.project-governor/state/`.

## Changed

- `task-router` is now the single source of truth for route, confidence, risk score, guardrails, workflow, and evidence requirement.
- `gpt55-auto-orchestrator` is now a runtime planner that wraps `task-router` instead of reclassifying tasks.
- Standard feature routes include `test-first-synthesizer` by default.
- Context pack builder prefers `CONTEXT_INDEX.json` before bounded repo scan.

## Migration

Run from repo root:

```bash
python3 codex_project_governor_harness_v6_upgrade.py --apply
python3 skills/context-indexer/scripts/build_context_index.py --project . --write
python3 skills/session-lifecycle/scripts/session_lifecycle.py start --project . --task-id harness-v6-smoke --route standard_feature
python3 skills/harness-doctor/scripts/doctor.py --project . --execution-readiness
make test
```
