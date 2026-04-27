# Data Model

## Repository Data Shapes

This repository has no database or persisted application data model. Its data contracts are file-based.

## Core File Models

### `InitResult`

Defined in `tools/init_project.py`.

Fields:

- `mode`
- `target`
- `created`
- `preserved`
- `skipped`

### Guard Findings

Implementation and style guard scripts return:

- `status`
- `findings[]`

Each finding contains a `type`, `severity`, `message`, and supporting fields specific to the checker.

### DESIGN.md Token Summary

`skills/design-md-governor/scripts/lint_design_md.py` and adjacent helpers return parsed project design-system tokens from YAML front matter plus section summaries from the Markdown body.

Primary fields include:

- `status`
- `summary`
- `findings[]`
- `designSystem`
- `token_counts`
- `sections`
- `regression`

### Upgrade Candidate Analysis

`skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py` returns:

- `status`
- `project_requirements`
- `summary`
- `candidates[]`
- `policy`

Each candidate includes current/candidate versions, semantic distance, skipped version count, relevance, risk, recommendation, score, reasons, and user choices.

### Harness v6 State

`skills/session-lifecycle/scripts/session_lifecycle.py` maintains project-local state under `.project-governor/state/`.

Core files:

- `SESSION.json`: current task session, route, target files, git status snapshot, and evidence path.
- `FEATURES.json`: feature registry placeholder.
- `AGENTS.json`: agent registry placeholder.
- `ISSUES.json`: issue registry placeholder.
- `QUALITY_SCORE.json`: quality score placeholder.
- `PROGRESS.md`: append-only session progress log.

### Harness v6 Evidence

`skills/evidence-manifest/scripts/write_evidence_manifest.py` writes `project-governor-evidence-v1` manifests under `.project-governor/evidence/<task-id>/EVIDENCE.json`.

Primary fields include:

- `task_id`
- `route`
- `acceptance_criteria[]`
- `tests[]`
- `reviews`
- `docs_refresh`

### Context Index v2

`skills/context-indexer/scripts/build_context_index.py` writes `project-governor-context-index-v2`.

Entries include path, size, mtime, hash, language, roles, symbols, imports, headings, tokens, summary, sensitivity flag, and stale reason.

### Memory Classification

`skills/memory-compact/scripts/classify_memory_items.py` returns an array of:

- `text`
- `classification`

Known classifications include durable facts, decisions, open questions, repeated mistakes, risks, stale items, temporary notes, and sensitive items.

## Template Memory Tables

Root governance memory uses Markdown tables under:

- `docs/memory/PROJECT_MEMORY.md`
- `docs/memory/OPEN_QUESTIONS.md`
- `docs/memory/RISK_REGISTER.md`
- `docs/memory/REPEATED_AGENT_MISTAKES.md`

Entries must include date, status, source, and evidence.
