---
name: convention-miner
description: Mine repository conventions such as stack, directory layout, components, API shape, tests, naming, style, architecture boundaries, and package manager from existing code.
---

# Convention Miner

Use this as a read-only audit before initializing governance docs or planning a non-trivial change.

## Rules

- Do not change files.
- Prefer evidence over inference.
- Cite file paths for every convention.
- Separate confirmed conventions from guesses.
- Identify conflicting conventions and stale patterns.
- Return a compact summary suitable for `docs/conventions/*`.

## Areas to inspect

- package manager and lockfiles
- framework and language stack
- directory structure and module boundaries
- component and naming conventions
- API contracts and error formats
- data fetching and state management
- design tokens and styling system
- tests, fixtures, mocks, and CI commands
- lint, typecheck, and formatting commands

## Output format

```markdown
# Convention Mining Report

## Confirmed conventions

| Area | Convention | Evidence |
|---|---|---|

## Conflicts

| Area | Conflict | Evidence | Recommendation |
|---|---|---|---|

## Unknowns

- <question>

## Candidate rules for AGENTS.md

- <rule>
```
