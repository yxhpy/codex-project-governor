---
name: harness-doctor
description: Diagnose Project Governor Harness v6 install shape, context index, state files, evidence gates, route guard scripts, and execution readiness.
---

# Harness Doctor

Use this skill when upgrading, reinstalling, or diagnosing a governed project.

Checks include:

- plugin manifest version and skill directory shape
- context-index v2 and docs-manifest presence and freshness metadata
- state files under `.project-governor/state`
- route guard diff collector presence
- Python script compile readiness

Run:

```bash
python3 skills/harness-doctor/scripts/doctor.py --project .
```
