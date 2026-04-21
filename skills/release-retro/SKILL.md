---
name: release-retro
description: After a release, summarize changes, incidents, risks, decisions, and memory updates into release retro documents.
---

# Release Retro

Use after a release or milestone.

## Inputs

- release notes
- git log / PR list
- incident reports
- test/CI failures
- user-facing behavior changes
- migration notes
- tasks retrospectives

## Process

1. Summarize what shipped.
2. Identify user-facing changes.
3. Identify technical changes.
4. Identify incidents, regressions, and mitigations.
5. Extract durable facts for `docs/memory/PROJECT_MEMORY.md`.
6. Extract decisions for `docs/decisions/`.
7. Extract open questions for `docs/memory/OPEN_QUESTIONS.md`.
8. Extract risks for `docs/memory/RISK_REGISTER.md`.
9. Do not modify application code.

## Output

Return a release retro and a memory update summary.
