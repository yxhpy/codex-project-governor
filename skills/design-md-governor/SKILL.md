---
name: design-md-governor
description: Adopt Google Labs Code DESIGN.md as an opt-in design-system source of truth for UI/style work; lint, summarize, diff, and generate migration guidance without copying design assets into projects by default.
---

# DESIGN.md Governor

## Purpose

Use Google's DESIGN.md-style design-system format as an opt-in source of truth for UI, visual identity, component styling, spacing, typography, colors, and design-token decisions.

This skill is used when the user asks to:

- introduce Google-style DESIGN.md governance
- create, lint, summarize, or compare a `DESIGN.md`
- align UI implementation with design tokens and rationale
- detect visual token drift before UI changes
- generate an agent-readable design summary
- migrate existing style docs or component registries toward a DESIGN.md source of truth

## Core rule

Do not create or overwrite project `DESIGN.md` automatically.

A project may opt in by explicitly choosing to add a project-owned `DESIGN.md`. Until then, this skill can lint or summarize an existing file and recommend an adoption plan.

## Source model

`DESIGN.md` contains two layers:

1. YAML front matter with machine-readable design tokens.
2. Markdown body with human-readable rationale and usage guidance.

Tokens are normative. Prose explains how and why to apply them.

## Project hygiene

This skill keeps plugin-level support files in the plugin:

- `skills/design-md-governor/**`
- `managed-assets/design-md/**`
- `examples/design-md-*.md`
- `tests/test_design_md_governor.py`

Project-owned files are created only when the user explicitly opts in:

- `DESIGN.md`
- `docs/design/DESIGN_MD_ADOPTION_PLAN.md`
- `tasks/<task>/DESIGN_MD_REPORT.md`

Do not add `.codex/agents`, `.codex/prompts`, plugin source folders, or global runtime assets to the target project as part of DESIGN.md adoption.

## Workflow

### 1. Detect

Look for project-owned design-system files:

- `DESIGN.md`
- `docs/design/DESIGN.md`
- `docs/conventions/UI_STYLE.md`
- `docs/conventions/COMPONENT_REGISTRY.md`
- `docs/conventions/PATTERN_REGISTRY.md`

If no `DESIGN.md` exists, recommend opt-in adoption rather than creating one silently.

### 2. Lint

Prefer the official CLI when available:

```bash
npx @google/design.md lint DESIGN.md
```

Fallback to the bundled deterministic linter when the CLI is unavailable:

```bash
python3 skills/design-md-governor/scripts/lint_design_md.py DESIGN.md
```

### 3. Summarize

For agent workflows, summarize the current design tokens and sections:

```bash
python3 skills/design-md-governor/scripts/summarize_design_md.py DESIGN.md
```

### 4. Compare

For changes to `DESIGN.md`, compare before/after and block regressions:

```bash
python3 skills/design-md-governor/scripts/diff_design_md.py DESIGN.before.md DESIGN.md
```

### 5. Apply to implementation

Before UI implementation, use the summary to constrain:

- colors
- typography
- spacing
- radius/shape
- component tokens
- do/don't guidance

If a requested UI change violates `DESIGN.md`, stop and ask whether to update `DESIGN.md` through a separate design-system iteration.

## Route integration

- `micro_patch`: read `DESIGN.md` only if the target file already uses design tokens or if the user explicitly references design tokens.
- `ui_change`: lint/summarize `DESIGN.md` when present.
- `standard_feature`: summarize `DESIGN.md` when UI is touched.
- `risky_feature`: do not treat visual design as sufficient validation; still run standard/risk checks.

## Output

Return:

- whether `DESIGN.md` exists
- lint status
- design-token summary
- implementation constraints
- warnings or blockers
- whether adoption/migration is recommended
- files that would be created only with user approval
