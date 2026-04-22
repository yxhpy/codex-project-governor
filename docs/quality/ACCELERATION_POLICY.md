# Quality-Gated Acceleration Policy

Use the acceleration pipeline when speed matters but quality gates still apply:

1. `task-router`
2. `context-pack-builder`
3. `pattern-reuse-engine`
4. `test-first-synthesizer`
5. `parallel-feature-builder`
6. `quality-gate`
7. `repair-loop` when needed
8. `merge-readiness`
9. `coding-velocity-report`

Do not use multiple write agents on overlapping production code. Do not skip quality gates for speed.
