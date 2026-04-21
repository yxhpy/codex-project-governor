---
name: implementation-guard
description: Check that a proposed implementation is minimal, iterative, and does not introduce rewrite risk, duplicate patterns, unapproved dependencies, unexplained new files, or public contract drift.
---

# Implementation Guard

Use after planning and before finalizing implementation.

## Checks

- rewrite risk: large replacement of existing files
- new dependencies: package additions require decision notes
- new files: every new file must be justified in the iteration plan
- duplicate patterns: new components/services/utilities must not duplicate registered ones
- API drift: response shapes and public behavior must remain stable unless approved
- docs updates: product, API, data model, architecture, memory, and decisions must be updated when applicable

## Deterministic helper

Use:

```bash
python3 skills/implementation-guard/scripts/check_iteration_compliance.py <json-input>
```

The input JSON may contain:

```json
{
  "rewrite_pct_by_file": {"src/file.ts": 0.45},
  "dependency_changes": ["new-package"],
  "new_files": ["src/new.ts"],
  "justified_new_files": [],
  "public_contract_changes": ["GET /api/users response shape changed"]
}
```

## Output

Return:

- pass/fail
- blocking issues
- warnings
- required patches
- documentation updates needed
