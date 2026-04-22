# Open Questions

Use this file for unresolved questions. Do not promote uncertain items to `PROJECT_MEMORY.md` until they are verified.

| Date | Question | Why it matters | Owner | Status | Evidence |
|---|---|---|---|---|---|
| 2026-04-21 | Should `tools/init_existing_project.py` keep accepting an unused `plugin_root` argument, or should the compatibility contract be revised? | The wrapper currently mutates `sys.path` and ignores `plugin_root`, which is brittle but may be compatibility behavior. | maintainer | open | `tools/init_existing_project.py` |
| 2026-04-21 | What exact threshold should require `tasks/<date>-<slug>/ITERATION_PLAN.md` in this repository? | The root iteration contract defines likely triggers, but small documentation-only patches may not need a plan. | maintainer | open | `docs/conventions/ITERATION_CONTRACT.md`, `templates/docs/conventions/ITERATION_CONTRACT.md` |
| 2026-04-21 | Should malformed helper-script inputs use a project-specific JSON error envelope? | Current behavior relies on standard Python and `argparse` errors, while normal successful outputs are structured JSON. | maintainer | open | `docs/architecture/API_CONTRACTS.md`, `skills/*/scripts/*.py` |
| 2026-04-21 | Should template docs remain generic placeholders, or should the plugin ship richer default examples? | Downstream initialization quality depends on useful templates, but overly specific defaults may mislead target repositories. | maintainer | open | `templates/docs/**`, `README.md` |
