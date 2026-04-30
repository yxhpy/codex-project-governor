---
name: init-existing-project
description: Initialize an existing repository for strict iterative Codex development by mining conventions and creating governance files without modifying application code, using automatic read-only subagent activation.
---

# Init Existing Project

Use this skill when code already exists and the goal is to make the project self-governing for future Codex sessions.

## Hard constraints

- Do not modify application code.
- Do not change dependencies.
- Do not re-architect the project.
- Do not rewrite existing docs unless the user explicitly allows it.
- Preserve existing style, structure, naming, component, API, and test conventions.
- Write only governance docs, task templates, Codex prompts, rules, and initialization reports.

## Required subagent workflow

Run `subagent-activation` with workflow `init-existing-project`.

Explicitly spawn selected read-only subagents only after host-runtime authorization is satisfied. If authorization is missing, ask once for consent; the user should not need to name agents. Each subagent must cite file paths, distinguish confirmed facts from guesses, avoid writing files, and return concise findings.

Preferred project-scoped roles:

1. `context-scout`: map directories, entrypoints, package boundaries, generated folders, and ignored folders.
2. `architecture-drift-reviewer`: infer architectural layers, dependency direction, service boundaries, and risky coupling.
3. `style-drift-reviewer`: infer naming, formatting, UI components, design tokens, and layout conventions.
4. `pattern-reuse-scout`: identify reusable patterns, services, hooks, schemas, and duplicate risks.
5. `test-planner`: infer test frameworks, test commands, test naming, fixtures, mocks, and coverage expectations.
6. `dependency-risk-reviewer`: identify package manager, lockfile, dependency patterns, duplicate libraries, and risky additions.
7. `docs-memory-reviewer`: infer product identity, durable facts, open questions, repeated mistakes, risks, and decision candidates.

## Consolidation

After all subagents finish:

1. Create governance files from templates.
2. Fill convention docs only with evidence-backed facts.
3. Put uncertain findings in `docs/memory/OPEN_QUESTIONS.md`.
4. Put risks in `docs/memory/RISK_REGISTER.md`.
5. Put repeated agent hazards in `docs/memory/REPEATED_AGENT_MISTAKES.md`.
6. Make `AGENTS.md` concise and prescriptive.
7. Do not put raw subagent notes into `AGENTS.md`; summarize durable rules only.

## Output

Return:

- files created
- files preserved
- conventions inferred
- unknowns requiring human review
- recommended next governance checks
- confirmation that no application code was modified
