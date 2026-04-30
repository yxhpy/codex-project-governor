# Quality-Gated Acceleration Policy

Fast routes reduce governance artifacts, not safety checks:

- `micro_patch`: direct edit, route guard, and light quality gate only. Do not create task plans, test plans, pattern reuse plans, evidence manifests, context packs, or subagent audits unless route guard fails and the work is rerouted.
- `tiny_patch`: direct edit, route guard, diff-scoped engineering standards, light quality gate, merge-readiness, and inline final-response evidence. Do not create task plans, test plans, pattern reuse plans, evidence manifests, context packs, or subagent audits unless the route escalates.

Standard pipeline: task-router, subagent-activation for non-trivial routes, context-pack-builder, pattern-reuse-engine, test-first-synthesizer, parallel-feature-builder, engineering-standards-governor for coding work, route-guard for fast routes, quality-gate, repair-loop, merge-readiness, coding-velocity-report.

Do not use multiple write agents on overlapping production code. Do not skip route guards or quality gates for speed. If a fast route exceeds its artifact policy or change budget, stop and reroute.
