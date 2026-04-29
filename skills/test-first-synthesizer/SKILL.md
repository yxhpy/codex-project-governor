---
name: test-first-synthesizer
description: Produce a targeted test plan or test skeletons before implementation, using existing project test style and covering behavior, regression risk, boundaries, and errors.
---

# Test-First Synthesizer

Use before or during implementation when the task affects behavior.

## Process

1. Read `CONTEXT_PACK.md` and related tests.
2. Identify test framework and naming style.
3. Cover normal behavior, boundary values, regression risks, error paths, and relevant integration/contract paths.
4. Create `TEST_PLAN.md`.

## Required test matrix

- normal behavior
- boundary values
- empty/null/error input
- regression case
- integration or contract behavior for external APIs, databases, auth, payment, queues, files, or browser boundaries
- frontend interaction, accessibility, loading, empty, and error states when UI changes
- explicit not-tested rationale for any relevant row intentionally skipped

## Mock governance

When mocks are necessary, record the real dependency or contract they represent and the integration, contract, smoke, or higher-level behavior test that protects the real path. Do not leave mocks, fixtures, or test data imported by production code.

## Do not

- delete failing tests
- weaken assertions without evidence
- introduce a new test framework without approval
