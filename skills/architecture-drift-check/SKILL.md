---
name: architecture-drift-check
description: Detect architecture drift, module boundary violations, import direction problems, unrecorded public contract changes, and undocumented data-model changes.
---

# Architecture Drift Check

Use before PRs, migrations, refactors, and public API changes.

## Required reading

- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/API_CONTRACTS.md`
- `docs/architecture/DATA_MODEL.md`
- `docs/conventions/PATTERN_REGISTRY.md`
- relevant nested `AGENTS.md` files

## Checks

- forbidden imports or dependency direction changes
- infrastructure leaking into domain logic
- UI depending directly on persistence internals
- API contract drift without docs
- data model drift without migration notes
- cross-module coupling not described in architecture docs
- new background jobs, side effects, queues, or external integrations without decisions

## Output

Return:

- blocking architecture drift
- warnings
- required ADR/PDR updates
- suggested minimal patch
