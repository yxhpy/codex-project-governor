# Quality-Gated Acceleration Policy

Use the acceleration pipeline when speed matters but quality gates still apply:

1. `task-router`
2. `context-pack-builder`
3. `pattern-reuse-engine`
4. `test-first-synthesizer`
5. `parallel-feature-builder`
6. `route-guard` for `micro_patch`, `tiny_patch`, and other fast-lane work
7. `quality-gate`
8. `repair-loop` when needed
9. `merge-readiness`
10. `coding-velocity-report`

Do not use multiple write agents on overlapping production code. Do not skip route guards or quality gates for speed.
