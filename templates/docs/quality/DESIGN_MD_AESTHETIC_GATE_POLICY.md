# DESIGN.md Aesthetic Gate Policy

This policy is an optional Project Governor project-level rule for UI/frontend work.

## Rule

Any task that creates or edits user-facing UI must use `$design-md-aesthetic-governor` before editing UI files.

The gate requires:

1. Gemini/Stitch design-service configuration from shell environment variables or project-root `.env-design`.
2. A project-owned `DESIGN.md`.
3. A successful preflight read proof at `.codex/design-md-governor/read-proof.json`.
4. Token-aware implementation using `DESIGN.md` values and rationale.
5. Post-edit drift verification.

Required design-service keys are `GEMINI_BASE_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, and `STITCH_MCP_API_KEY`. `GEMINI_PROTOCOL` may be `auto`, `openai`, or `gemini`; `STITCH_MCP_URL` defaults to `https://stitch.googleapis.com/mcp`. `.env-design` is local secret configuration and must not be committed. A user may intentionally use basic mode only with shell environment variable `DESIGN_BASIC_MODE=1`; legacy `DESIGN_ENV_SKIP=1` and `DESIGN_SERVICE_CONFIG_SKIP=1` are still accepted. Basic-mode flags in `.env-design` are not honored.

## Stitch / Gemini / GPT workflow

Full-service mode uses three roles:

1. GPT/Codex orchestrates the work, reads repository rules and `DESIGN.md`, edits code, and records evidence.
2. Stitch MCP supplies visual prototype or screen exploration support when the task asks for a prototype, redesign, or visual direction, using remote MCP streamable HTTP by default.
3. Gemini supplies external design critique against `DESIGN.md`, checking hierarchy, consistency, and likely UX issues.

Basic mode skips Stitch and Gemini. GPT/Codex may still do frontend work using `DESIGN.md`, existing components, bundled lint, and drift checks.

The default Stitch path is the hosted remote MCP endpoint, so no local MCP package or Google Cloud CLI is required unless a project explicitly opts into a local Stitch MCP server.

Full-service tasks should run `design_service_review.py --task "<ui task>"` before implementation. That script records Gemini review evidence and Stitch MCP tool availability without creating remote Stitch projects.

## Hook enforcement

When Codex hooks are enabled, `.codex/hooks/design_md_codex_hook.py` blocks common UI edit paths until design-service configuration is present and read proof exists and matches the current `DESIGN.md`.

Hooks are guardrails. They do not replace final QA, tests, accessibility checks, or human design review.
