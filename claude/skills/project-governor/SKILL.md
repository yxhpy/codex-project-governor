---
name: project-governor
description: Use Project Governor Harness workflows inside Claude Code for iterative coding, context indexing, governed memory search, route guards, evidence gates, engineering standards, upgrades, and DESIGN.md UI gates.
---

# Project Governor For Claude Code

Use this skill when a Claude Code session should follow Project Governor rules instead of ad hoc coding.

## Source Of Truth

- Project rules: read `CLAUDE.md` first; initialized projects import `AGENTS.md`.
- Plugin workflows: `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/SKILL.md`.
- Deterministic scripts: `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/` and `${CLAUDE_PLUGIN_ROOT}/tools/`.
- Target-project state: `.project-governor/`.

Do not copy plugin-global assets into a target repository. Use `templates/` only through the initializer or upgrade migrator.

## Default Workflow

1. For non-trivial coding, classify the request:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/task-router/scripts/classify_task.py" --request "$ARGUMENTS"
   ```

2. Query compact project context before opening large docs:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/context-indexer/scripts/query_context_index.py" --project . --request "$ARGUMENTS" --auto-build
   ```

3. Build a task context pack and reuse plan before creating new files or patterns.
4. Use the smallest coherent patch that preserves adjacent project conventions.
5. Run engineering standards and quality gate checks before final response.
6. Record session learning when commands fail, an assumption is corrected, or memory looks stale.

## Common Scripts

- Initialize governance files:
  `python3 "${CLAUDE_PLUGIN_ROOT}/tools/init_project.py" --mode existing --target . --json`
- Build context index:
  `python3 "${CLAUDE_PLUGIN_ROOT}/skills/context-indexer/scripts/build_context_index.py" --project . --write`
- Query governed memory:
  `python3 "${CLAUDE_PLUGIN_ROOT}/skills/context-indexer/scripts/query_context_index.py" --project . --request "<query>" --memory-search --auto-build`
- Run engineering standards:
  `python3 "${CLAUDE_PLUGIN_ROOT}/skills/engineering-standards-governor/scripts/check_engineering_standards.py" --project .`
- Run harness doctor:
  `python3 "${CLAUDE_PLUGIN_ROOT}/skills/harness-doctor/scripts/doctor.py" --project . --execution-readiness`

## Manual Slash Commands

Use the bundled `pg-*` commands for common entry points:

- `/pg-init`
- `/pg-route`
- `/pg-context`
- `/pg-quality`
- `/pg-memory`
- `/pg-upgrade`
- `/pg-design`
- `/pg-doctor`

## Safety

- Do not run destructive Git, delete, publish, or deployment commands unless the user explicitly asks.
- Do not add dependencies without an upgrade or dependency decision.
- Do not leave mock implementations in production paths.
- Do not write durable memory without date, status, source, and evidence.
