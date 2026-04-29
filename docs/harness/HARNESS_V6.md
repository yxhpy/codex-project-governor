# Project Governor Harness v6.0

Harness v6.0 upgrades Project Governor from skill collection to project harness.

## Runtime contract

```text
task-router = single route source of truth
gpt55-auto-orchestrator = runtime planner
context-indexer v2 = project-local context memory
session-lifecycle = state and handoff layer
memory-compact session learning = failed-command and stale-memory capture
route-guard = git-diff-derived guardrail facts
quality-gate = evidence-aware verification gate
merge-readiness = evidence-based final readiness
harness-doctor = install and execution diagnosis
```

## Required project state

```text
.project-governor/state/
  FEATURES.json
  AGENTS.json
  ISSUES.json
  COMMAND_LEARNINGS.json
  MEMORY_HYGIENE.json
  PROGRESS.md
  SESSION.json
  QUALITY_SCORE.json
```

## Required evidence for non-trivial work

```text
.project-governor/evidence/<task-id>/
  EVIDENCE.json
  ACCEPTANCE_MAP.md
  TEST_LOG.txt (optional)
```

## Reading policy

Do not read all initialization documents at session start. Read `AGENTS.md`, read `DOCS_MANIFEST.json` and the session brief when present, query the context index, run memory search for prior failures and stale-memory notes related to the request, and only then read task-specific section line ranges. Open full documents only when section results are insufficient, confidence is low, or the change touches a public contract/template source of truth.

Docs marked `stale` or `superseded` are avoid-by-default. Use `--include-stale` only for history, cleanup, or migration review tasks.

Before ending a non-trivial session, record failed commands, repeated mistakes, corrected assumptions, and stale-memory candidates with `record_session_learning.py` so the next session can retrieve them.
