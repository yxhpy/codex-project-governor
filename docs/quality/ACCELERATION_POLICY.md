# Quality-Gated Acceleration Policy

Use the acceleration pipeline when speed matters but quality gates still apply.

Fast routes reduce governance artifacts, not safety checks:

- `micro_patch`: direct edit, route guard, and light quality gate only. Do not create task plans, test plans, pattern reuse plans, evidence manifests, context packs, or subagent audits unless route guard fails and the work is rerouted.
- `tiny_patch`: direct edit, route guard, diff-scoped engineering standards, light quality gate, merge-readiness, and inline final-response evidence. Do not create task plans, test plans, pattern reuse plans, evidence manifests, context packs, or subagent audits unless the route escalates.

Use the standard acceleration pipeline for non-fast routes:

1. `task-router`
2. `subagent-activation` when the routed workflow is non-trivial
3. `context-pack-builder`
4. `pattern-reuse-engine`
5. `test-first-synthesizer`
6. `parallel-feature-builder`
7. `engineering-standards-governor` for coding work
8. `route-guard` for `micro_patch`, `tiny_patch`, and other fast-lane work
9. `quality-gate`
10. `repair-loop` when needed
11. `merge-readiness`
12. `coding-velocity-report`

Do not use multiple write agents on overlapping production code. Do not skip route guards or quality gates for speed. If a fast route exceeds its artifact policy or change budget, stop and reroute instead of creating heavy artifacts under the original route.
