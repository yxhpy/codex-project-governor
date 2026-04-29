# Engineering Standards Policy

Project Governor treats engineering standards as part of the quality gate, not optional style preference.

## Scope

Apply this policy when a task changes production code, test code, build/runtime scripts, public API contracts, frontend UI behavior, or backend service logic.

Docs-only changes may skip the source scanner, but must still record why no code checks were relevant.

## Maintainability thresholds

Default thresholds:

| Rule | Warning | Blocking |
|---|---:|---:|
| Source file length | > 400 lines | > 800 lines |
| Function length | > 60 lines | > 100 lines |
| Approximate function complexity | > 10 | > 15 |

If a project needs tighter thresholds, record them in `docs/conventions/CONVENTION_MANIFEST.md`.
Looser thresholds require an ADR/PDR with migration rationale.

## Reuse-first rule

Before adding new components, services, hooks, schemas, helpers, fixtures, or test utilities:

1. Run or consult `pattern-reuse-engine`.
2. Record required reuse and forbidden duplicates in `tasks/<task>/PATTERN_REUSE_PLAN.md`.
3. Justify every new pattern in `ITERATION_PLAN.md`.

Creating a parallel implementation to avoid understanding existing code is a quality failure.

## Backend and API expectations

- Keep public request/response shapes stable unless the iteration plan and API contracts approve the change.
- Keep domain logic out of controllers/routes when an existing service or use-case layer exists.
- Prefer typed/validated boundaries over ad hoc string parsing.
- Cover normal behavior, boundary values, validation errors, permission failures, and integration/contract paths for external systems.

## Frontend expectations

- Reuse existing components, hooks, tokens, layouts, routes, and data-loading patterns.
- Avoid new styling systems or component libraries without upgrade advisory and approval.
- Cover visible states: loading, empty, success, error, permission denied, and responsive layout when relevant.
- UI work must also follow the applicable DESIGN.md governance policy.

## Mock governance

Production code must not import mocks, fixtures, test data, or test-only libraries such as `__mocks__`, `fixtures`, `testdata`, `tests`, `.mock.*`, `.fixture.*`, `msw`, `faker`, or `@faker-js/faker`.

When mock data is used in tests:

- keep it under test/fixture paths
- name it clearly as test data
- record which real API, service, or contract it represents
- add an integration, contract, or smoke test when the mock protects an external dependency

Leftover production identifiers such as `mockData`, `fakeUser`, `demoData`, or `sampleResponse` require review.

## Test planning

`TEST_PLAN.md` must cover relevant rows:

| Case | Required when |
|---|---|
| Normal behavior | Any behavior change |
| Boundary values | Inputs, limits, pagination, money, dates, sizes, permissions |
| Empty/null/error input | Any input parsing or API handling |
| Regression | Fixes and risk-prone changes |
| Integration/contract | External API, database, queue, auth, payment, file, or browser boundary |
| Frontend interaction | UI state, accessibility, responsive, routing, or form behavior |
| Not tested rationale | Any relevant row intentionally skipped |

Tests must assert behavior. A test file that defines cases without assertions is incomplete unless it is an approved compile/smoke harness and the reason is recorded.

## Deterministic check

Run:

```bash
python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project .
```

For branch work, prefer diff scope:

```bash
python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --diff-base main
```

Diff scope reports findings introduced by added files, untracked source files, or changed lines so existing debt can be tracked separately from the current patch. Use full-project scope when intentionally auditing accumulated debt.

Record the result in `ENGINEERING_STANDARDS_REPORT.md` and feed the JSON into `quality-gate` as `engineering_standards` when using a quality-gate input file.
