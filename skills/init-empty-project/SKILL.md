---
name: init-empty-project
description: Initialize a new repository with Codex governance docs, memory layers, task templates, prompts, rules, and iteration-first constraints without creating application code.
---

# Init Empty Project

Use this skill when the repository is empty or before application code exists.

## Goal

Create a governance foundation before code is written, so future Codex sessions inherit project identity, memory policy, development rules, and iteration constraints.

## Hard constraints

- Do not create application code.
- Do not choose a stack unless the user provided one.
- Do not invent product facts beyond the user's input.
- Mark unknowns as open questions.
- Create only governance files, memory files, decision templates, task templates, Codex prompts, hooks, and rules.

## Required output tree

Create or preserve:

- `AGENTS.md`
- `docs/project/CHARTER.md`
- `docs/project/PRODUCT_SPEC.md`
- `docs/project/ROADMAP.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/conventions/ITERATION_CONTRACT.md`
- `docs/conventions/CODE_STYLE.md`
- `docs/conventions/UI_STYLE.md`
- `docs/conventions/PATTERN_REGISTRY.md`
- `docs/conventions/COMPONENT_REGISTRY.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/API_CONTRACTS.md`
- `docs/architecture/DATA_MODEL.md`
- `docs/memory/PROJECT_MEMORY.md`
- `docs/memory/OPEN_QUESTIONS.md`
- `docs/memory/REPEATED_AGENT_MISTAKES.md`
- `docs/memory/RISK_REGISTER.md`
- `docs/decisions/ADR-0000-template.md`
- `docs/decisions/PDR-0000-template.md`
- `tasks/_template/ITERATION_PLAN.md`
- `tasks/_template/EXECUTION_LOG.md`
- `tasks/_template/RETRO.md`
- `.codex/prompts/memory-compact.md`
- `.codex/prompts/pr-governance-review.md`
- `.codex/rules/project.rules`

## Process

1. Read any user-provided project facts.
2. Create governance files from templates.
3. Fill only fields supported by user-provided facts.
4. Place unknowns into `docs/memory/OPEN_QUESTIONS.md`.
5. Do not initialize an app, framework, package manager, or dependency tree.
6. Return a summary of files created and fields requiring human completion.

## Done when

- The repository has a valid `AGENTS.md`.
- The repository has project, convention, architecture, memory, decision, and task template files.
- The first development task can be planned through `iteration-planner`.
