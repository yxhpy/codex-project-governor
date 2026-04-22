# DESIGN.md Policy

`DESIGN.md` is an opt-in project-owned source of truth for visual identity and design tokens.

## Rules

- Do not create `DESIGN.md` unless the user explicitly opts in.
- When present, read `DESIGN.md` before UI/style implementation.
- Do not introduce raw colors, spacing, radius, or typography values that conflict with `DESIGN.md`.
- If implementation requires a new design token, plan a design-system update first.
- Do not treat plugin-managed `managed-assets/design-md/*` as project-owned files.

## Validation

Prefer the official Google Labs Code CLI when available:

```bash
npx @google/design.md lint DESIGN.md
```

Fallback:

```bash
python3 skills/design-md-governor/scripts/lint_design_md.py DESIGN.md
```
