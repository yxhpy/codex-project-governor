---
name: style-drift-check
description: Detect UI, component, naming, formatting, token, layout, and visual style drift against the project convention registry.
---

# Style Drift Check

Use before PRs, after UI changes, and during scheduled governance checks.

## Required reading

- `docs/conventions/UI_STYLE.md`
- `docs/conventions/COMPONENT_REGISTRY.md`
- `docs/conventions/CODE_STYLE.md`
- adjacent existing components

## Checks

- raw colors or unregistered design tokens
- duplicated components
- new component names not added to registry
- new styling systems or layout primitives
- CSS-in-JS / Tailwind / CSS module drift against current pattern
- naming and casing drift
- inconsistent error, empty, and loading states

## Deterministic helper

Use:

```bash
python3 skills/style-drift-check/scripts/check_style_drift.py <json-input>
```

## Output

Return:

- pass/fail
- style drift findings
- evidence paths
- smallest corrective patch
