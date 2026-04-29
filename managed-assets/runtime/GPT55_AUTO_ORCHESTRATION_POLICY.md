# GPT-5.5 Auto Orchestration Policy

## Purpose

Use GPT-5.5 as the default high-capability Codex model while reducing user prompt burden, repeated document reads, unnecessary subagents, and token waste.

## Model routing

- Use `gpt-5.5` for implementation, risk, review, research, and tool-heavy work.
- Use `gpt-5.4-mini` for read-only scouting and low-risk micro-patch classification.
- Use `gpt-5.4` as fallback when GPT-5.5 is unavailable during rollout.

## Context routing

At session start, do not read all initialization docs. Prefer:

1. `.project-governor/context/DOCS_MANIFEST.json`
2. `.project-governor/context/SESSION_BRIEF.md`
3. `.project-governor/context/CONTEXT_INDEX.json`
4. task-specific section query with `recommended_sections`
5. full documents only when sections are insufficient
6. only then broader scanning

## Skill routing

The orchestrator should infer and invoke Project Governor skills automatically. The user should not need to manually list `task-router`, `subagent-activation`, `context-pack-builder`, or `quality-gate`.

## Subagent routing

- `micro_patch`: no subagents.
- `standard_feature`: optional read-only subagents.
- `risky_feature`, `upgrade`, `research`, `migration`: required subagents.

## Clean reinstall compatibility

`clean-reinstall-manager` may apply this mode to one project or all governed projects by writing project-owned `.project-governor/runtime/*` files and context indexes. It must not copy plugin-global assets into target projects.
