---
name: evidence-manifest
description: Create and validate Harness v6 evidence manifests that map acceptance criteria, commands, reviews, and docs-refresh decisions to merge readiness.
---

# Evidence Manifest

Use this skill before declaring non-trivial work complete.

The evidence manifest is the Project Governor Harness v6 system of record for:

- acceptance criteria and proof mapping
- test or verification commands and outcomes
- spec-compliance and code-quality review results
- docs-refresh decisions
- route, risk, and task identity

Default path:

```text
.project-governor/evidence/<task-id>/EVIDENCE.json
```

A task is not merge-ready when the selected route requires evidence and the manifest is missing or incomplete.
