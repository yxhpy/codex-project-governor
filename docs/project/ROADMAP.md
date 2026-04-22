# Roadmap

## Current Phase

Governance plugin v0.3.0 with initialized self-governance and advisory research gates for this source repository.

## Current Maintained Surfaces

- Plugin metadata and public README.
- Skill documentation under `skills/`.
- Deterministic helper scripts under `tools/` and `skills/*/scripts/`.
- Governance templates under `templates/`.
- Example inputs and scheduled-memory examples under `examples/`.
- Self-test workflow under `tests/` and `.github/workflows/selftest.yml`.

## Near-Term Priorities

- Keep self-tests aligned with every new skill, template, and helper script.
- Keep research and release-research policies aligned with the advisory-only upgrade model.
- Fill root governance docs only with facts confirmed from repository evidence.
- Preserve dependency-free Python helper scripts unless an explicit decision approves a new dependency.
- Tighten public CLI contracts when helper scripts change.

## Later Candidates

- Add stronger contract tests for helper-script error behavior.
- Decide whether research registers should gain deterministic validation.
- Clarify thresholds for when a change requires a task iteration plan.
- Decide whether template docs should remain generic or include richer default guidance.

## Evidence

- `.codex-plugin/plugin.json` declares version `0.3.0`.
- `README.md` lists 13 skills and deterministic script entrypoints.
- `.github/workflows/selftest.yml` runs the repository self-test on push, pull request, and workflow dispatch.
