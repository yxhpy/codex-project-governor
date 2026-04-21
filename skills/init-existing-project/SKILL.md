---
name: init-existing-project
description: Initialize an existing repository for strict iterative Codex development by mining conventions and creating governance files without modifying application code.
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

Explicitly spawn read-only subagents. Each subagent must cite file paths, distinguish confirmed facts from guesses, avoid writing files, and return concise findings.

1. `repo-cartographer`: map directories, entrypoints, package boundaries, generated folders, and ignored folders.
2. `architecture-archeologist`: infer architectural layers, dependency direction, service boundaries, and risky coupling.
3. `style-miner`: infer naming, formatting, error handling, logging, async, state, and data-fetching patterns.
4. `component-miner`: infer UI components, design tokens, layout conventions, and reusable patterns.
5. `test-miner`: infer test frameworks, test commands, test naming, fixtures, mocks, and coverage expectations.
6. `dependency-risk-miner`: identify package manager, lockfile, dependency patterns, duplicate libraries, and risky additions.
7. `api-contract-miner`: infer API routes, schema, response shapes, status codes, and error formats.
8. `product-doc-miner`: infer product identity from README, docs, route names, UI copy, examples, and comments.
9. `memory-candidate-miner`: find durable facts, open questions, repeated mistakes, risks, and decision candidates.

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
