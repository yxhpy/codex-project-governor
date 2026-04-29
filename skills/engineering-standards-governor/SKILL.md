---
name: engineering-standards-governor
description: Enforce practical backend/frontend engineering standards, source size limits, function complexity thresholds, mock leakage checks, and test hygiene before quality-gate completion.
---

# Engineering Standards Governor

Use for coding tasks that add or change production or test code.

## Purpose

Catch maintainability and test-quality drift before it becomes project debt:

- files that are too large
- functions that are too long or too complex
- production code importing mocks, fixtures, test data, or test-only libraries
- mock-like demo data left in production paths
- tests that define cases without assertions
- new implementation patterns that should reuse existing components, services, hooks, schemas, fixtures, or tests

## Process

1. Read the task context pack, pattern reuse plan, and test plan when present.
2. Run the deterministic checker against the project or the current diff:

   ```bash
   python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --diff-base main
   ```

3. Review blockers before finalizing implementation.
4. Put the JSON summary or a human summary in `tasks/<task>/ENGINEERING_STANDARDS_REPORT.md`.
5. Feed the result into `quality-gate` as the `engineering_standards` check when using a quality-gate input file.

## Default thresholds

- source file line count: warn above 400, block above 800
- function line count: warn above 60, block above 100
- approximate cyclomatic complexity: warn above 10, block above 15

Project-specific policy may tighten these values, but loosening them requires an explicit decision record.

## Mock governance

- Production files must not import from `__mocks__`, `fixtures`, `testdata`, `tests`, `.mock.*`, `.fixture.*`, `msw`, `faker`, or `@faker-js/faker`.
- Temporary mock data is allowed only in tests, examples, fixtures, or documented non-production scaffolding.
- If a feature uses mocks for an external dependency, the task must also record the contract, integration, or smoke test that protects the real path.

## Test planning requirements

Before or during implementation, ensure the test plan covers the relevant rows:

- normal behavior
- boundary values
- empty/null/error input
- permission/auth failures when applicable
- integration or contract behavior for external APIs
- regression case for the reported bug or risk
- frontend interaction/accessibility path when UI changes
- explicit rationale for anything intentionally not tested

## Do not

- bypass findings by moving production mocks into differently named files
- delete or weaken tests to pass the gate
- add a new framework, dependency, test runner, or mock library without upgrade advisory and approval
- create a duplicate component/service/helper when `pattern-reuse-engine` found an existing candidate
