# Quality-Gated Acceleration Policy

Use the acceleration pipeline when speed matters but quality gates still apply:

1. `task-router`
2. `subagent-activation` when the routed workflow is non-trivial
3. `context-pack-builder`
4. `pattern-reuse-engine`
5. `test-first-synthesizer`
6. `parallel-feature-builder`
7. `route-guard` for `micro_patch`, `tiny_patch`, and other fast-lane work
8. `quality-gate`
9. `repair-loop` when needed
10. `merge-readiness`
11. `coding-velocity-report`

Do not use multiple write agents on overlapping production code. Do not skip route guards or quality gates for speed.
