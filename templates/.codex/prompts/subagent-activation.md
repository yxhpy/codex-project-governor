Use @project-governor subagent-activation.

Input:
- current task route
- workflow or skill name
- quality level
- confidence
- risk signals
- whether target is shared/global

Rules:
- Do not ask the user to list subagents.
- Return `none`, `optional`, or `required`.
- Select project-scoped custom agents from `.codex/agents/` when present.
- Use gpt-5.4-mini for fast read-only scouting.
- Use gpt-5.4 for implementation, risk, architecture, repair, and final quality review.
- Explicitly spawn selected subagents when mode is `required`.
- Wait for all read-only subagents before writing implementation code.
- For `micro_patch`, do not spawn subagents unless route-guard fails or the target unexpectedly touches shared/global scope.
