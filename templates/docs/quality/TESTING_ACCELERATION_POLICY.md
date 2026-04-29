# Testing Acceleration Policy

Reuse existing test style, prefer targeted behavior tests, cover regression and error paths, and do not delete or weaken tests to pass.

Every non-trivial `TEST_PLAN.md` must identify normal, boundary, error, regression, integration/contract, frontend interaction, and not-tested rationale rows that apply to the change.

Mocks are allowed only when the real dependency boundary is named and a contract, integration, smoke, or higher-level behavior test protects the real path. Do not leave mock or fixture imports in production code.
