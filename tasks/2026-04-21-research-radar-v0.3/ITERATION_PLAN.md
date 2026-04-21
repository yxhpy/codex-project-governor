# Iteration Plan

## User request

Apply `/Users/yxhpy/Downloads/codex-project-governor-add-research-radar-v0.3.patch`.

## Existing behavior

Project Governor v0.2.0 includes governance initialization, convention mining, iteration planning, drift checks, release retros, memory compaction, and upgrade advisory support. It does not yet include advisory research gates for candidate capabilities or release-version evidence.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
|---|---|---|
| Skill workflow metadata | `skills/*/SKILL.md` | New skills use front matter with `name` and `description`. |
| Dependency-free deterministic scripts | `skills/*/scripts/*.py` | New helpers use Python standard library only and print JSON. |
| Example JSON fixtures | `examples/*.json` | New research helpers use checked-in fixtures for self-tests. |
| Template prompts and docs | `templates/.codex/prompts/`, `templates/docs/` | New downstream governance files live under existing template paths. |
| Self-test coverage | `tests/selftest.py` | New skills, templates, and helper outputs are validated in the existing unittest suite. |

## Files expected to change

- `.codex-plugin/plugin.json`
- `README.md`
- `docs/architecture/API_CONTRACTS.md`
- `tests/selftest.py`
- `templates/AGENTS.md`
- `templates/docs/conventions/CONVENTION_MANIFEST.md`

## Files not to change

- Application source paths outside governance surfaces.
- Package manifests, lockfiles, dependency files, and service/runtime configuration.
- Existing deterministic helper output shapes.

## New files

| File | Why existing files cannot cover it |
|---|---|
| `docs/research/V0.3_RESEARCH_BRIEF.md` | Captures the v0.3 research-gate rationale separately from durable memory. |
| `examples/research-candidates.json` | Provides a deterministic fixture for research candidate scoring. |
| `examples/version-research-manifest.json` | Provides a deterministic fixture for version research. |
| `skills/research-radar/SKILL.md` | Defines a reusable advisory workflow for candidate capability research. |
| `skills/research-radar/scripts/score_research_candidates.py` | Provides offline scoring so research ranking is testable. |
| `skills/version-researcher/SKILL.md` | Defines a reusable advisory workflow before upgrade-advisor. |
| `skills/version-researcher/scripts/research_versions.py` | Provides offline version evidence analysis so release research is testable. |
| `templates/.codex/prompts/research-radar.md` | Copies a ready prompt into governed target repositories. |
| `templates/.codex/prompts/version-researcher.md` | Copies a ready prompt into governed target repositories. |
| `templates/docs/research/RESEARCH_POLICY.md` | Adds downstream source policy and research write boundary. |
| `templates/docs/research/RESEARCH_REGISTER.md` | Adds downstream research decision tracking. |
| `templates/docs/upgrades/RELEASE_RESEARCH_POLICY.md` | Adds downstream release-evidence policy before upgrades. |
| `templates/docs/upgrades/RELEASE_RESEARCH_REPORT.md` | Adds downstream release research report structure. |

## Dependencies

No new dependencies. The new scripts use only the Python standard library.

## Tests

- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`
- `python3 tools/init_project.py --mode existing --target <tmpdir> --json`

## Risks

- The supplied patch does not apply cleanly to the current manifest and self-test files, so those hunks must be rebased manually.
- New subagent wording must remain compatible with Codex's explicit-delegation requirement.
- New helper output contracts must be documented to avoid hidden JSON contract drift.

## Rollback

Revert the v0.3 manifest/README/test updates and delete the new research skill, fixture, prompt, template, and task-plan files from this iteration.
