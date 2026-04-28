# Iteration Plan: DESIGN.md Aesthetic Governor Patch

## Request

Apply the local Downloads Project Governor patch:

- `/Users/yxhpy/Downloads/codex-project-governor-v6.0.0-design-md-aesthetic-governor.patch`

Finalize it as the `6.0.1` repository patch release.

## Upgrade advisory

- Current plugin version: `6.0.0`
- Candidate version: `6.0.1`
- Candidate patch: `6.0.0-design-md-aesthetic-governor`
- Version distance: same base version, additive capability patch
- Requirement relevance: requested directly by the user from Downloads
- Recommendation: `recommend_upgrade`

## Existing patterns reused

- Skill workflows live under `skills/<skill>/SKILL.md`.
- Deterministic helper scripts live under `skills/*/scripts/`.
- Plugin-owned examples live under `examples/`.
- Project-owned templates live under `templates/`.
- Quality policy docs live under `docs/quality/`.
- Release notes and feature metadata live under `releases/`.
- Tests use Python standard-library `unittest`.

## Files expected to change

- `.codex/config.toml`
- `.codex/hooks.json`
- `.codex/hooks/design_md_codex_hook.py`
- `docs/quality/DESIGN_MD_AESTHETIC_GATE_POLICY.md`
- `examples/design-md-aesthetic-example.md`
- `releases/*design-md-aesthetic*`
- `skills/design-md-aesthetic-governor/**`
- `skills/design-md-aesthetic-governor/scripts/design_env_check.py`
- `skills/design-md-aesthetic-governor/scripts/design_service_smoke.py`
- `skills/design-md-aesthetic-governor/scripts/design_service_review.py`
- `.mcp.json`
- `templates/.codex/**`
- `templates/docs/quality/DESIGN_MD_AESTHETIC_GATE_POLICY.md`
- `tests/test_design_md_aesthetic_governor.py`
- `Makefile`
- `README.md`
- `.codex-plugin/plugin.json`
- `CHANGELOG.md`
- `releases/6.0.1.md`
- `releases/FEATURE_MATRIX.json`
- `releases/MIGRATIONS.json`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/upgrades/UPGRADE_REGISTER.md`

## Files not to change

- Existing initializer copy paths unless tests show they must change.
- Existing deterministic JSON output schemas.
- Existing memory and decision files unless durable facts need recording.
- Existing plugin version unless a release decision explicitly requires it.

## Conflict handling

The patch does not apply cleanly to `.codex/config.toml`, `.codex/hooks.json`, `templates/.codex/config.toml`, or `templates/.codex/hooks.json` because the local files are already expanded from one-line fixtures. Merge those files manually while preserving existing Stop hook behavior.

## Validation

- `python3 tests/test_design_md_aesthetic_governor.py`
- `python3 tests/selftest.py`
- `python3 -m compileall tools skills tests`
- `make test`
- real remote Stitch MCP initialize smoke with a dummy key
- real remote Stitch MCP tools/list smoke with a dummy key
- real Gemini endpoint auth smoke with a dummy key
- protocol dry-runs for native Gemini `generateContent` and OpenAI-compatible chat completions

## Risks

- Hook commands may be too strict for projects without adopted `DESIGN.md`, local design-service configuration, or explicit `DESIGN_BASIC_MODE=1`.
- `.env-design` may contain Gemini or Stitch API keys and must remain uncommitted.
- Real full-service smoke cannot be completed from automation unless credentials are supplied through local `.env-design` or shell environment without printing them.
- Gemini gateways may expose OpenAI-compatible `/v1/chat/completions` rather than native Gemini `generateContent`; `GEMINI_PROTOCOL` must make that explicit.
- New `.codex` hook configuration affects downstream initialized projects.
- README and manifest positioning must stay aligned with the new skill.

## Rollback

Revert this task's diff and remove the upgrade-register entry for the local patch.
