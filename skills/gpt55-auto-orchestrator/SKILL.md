---
name: gpt55-auto-orchestrator
description: Automatically choose Project Governor skills, subagents, model strategy, context budget, and quality gates for Codex GPT-5.5 without requiring the user to specify the workflow.
---

# GPT-5.5 Auto Orchestrator

## Purpose

Use GPT-5.5's stronger tool use, completion persistence, and coding/research ability without increasing user prompt burden.

This skill should be used automatically when the user asks to implement, fix, refactor, review, research, upgrade, initialize, refresh, or clean a Project Governor project.

## Core rule

The user should not need to know which Project Governor skill, subagent, model, or context workflow to invoke.

The orchestrator must:

1. infer the request type,
2. choose the smallest safe workflow,
3. query the context index before reading large docs,
4. activate subagents only when useful,
5. route model usage for speed, token economy, and quality,
6. run quality gates appropriate to risk,
7. avoid copying plugin-global assets into target projects.

## Model policy

Prefer:

- `gpt-5.5` for implementation, hard reasoning, tool-heavy workflows, code review, research synthesis, migrations, and risk assessment.
- `gpt-5.4-mini` for fast read-only scouting, context retrieval, simple lint-style classification, summaries, and low-risk subagents.
- `gpt-5.4` as fallback when `gpt-5.5` is unavailable.

Do not use high-reasoning GPT-5.5 for micro-patches unless route-guard escalates the task.

## Context policy

Do not read all initialization docs at session start.

Instead:

1. read `AGENTS.md` only when available and small,
2. read `.project-governor/context/DOCS_MANIFEST.json` if present,
3. read `.project-governor/context/SESSION_BRIEF.md` if present,
4. query `.project-governor/context/CONTEXT_INDEX.json`,
5. read returned `recommended_sections` line ranges before full documents,
6. read full files only when sections are insufficient or confidence is low,
7. escalate to `context-indexer` if the index is missing or stale.

## Workflow policy

Run the deterministic helper first when possible:

```bash
python3 skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py examples/gpt55-runtime-standard-feature.json
```

Then follow the returned `skill_sequence` and `subagents`.

## Output

Return:

- selected workflow,
- selected model plan,
- selected subagents,
- context budget,
- route doc pack,
- skill sequence,
- skipped skills with reasons,
- quality gate level,
- clean reinstall / latest mode actions when relevant.
