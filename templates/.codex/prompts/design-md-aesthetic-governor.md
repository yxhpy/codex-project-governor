# Codex prompts

## Adopt DESIGN.md first

```text
Use $design-md-aesthetic-governor.
This repo does not have a mature DESIGN.md. First verify Gemini/Stitch config from environment variables or project .env-design, or confirm DESIGN_BASIC_MODE=1. Then inspect the current UI, recommend 3 aesthetic references from the awesome-design-md catalog, and create docs/design/DESIGN_MD_ADOPTION_PLAN.md. Do not change production UI files yet.
```

## Build UI with the gate

```text
Use $design-md-aesthetic-governor.
Build <page/component>. Verify full-service Gemini/Stitch config or DESIGN_BASIC_MODE=1, read DESIGN.md, run preflight, choose an aesthetic reference only if the project design is underspecified, implement with token discipline, then run verify_design_usage.py and include DESIGN.md compliance in the final answer.
```

## Review UI drift

```text
Use $design-md-aesthetic-governor.
Review the uncommitted UI changes for DESIGN.md drift. Verify full-service Gemini/Stitch config or DESIGN_BASIC_MODE=1, run the lint and verification scripts, return blockers first, and do not rewrite unrelated code.
```
