<!-- generated_from: iteration_plan_v1; source: ITERATION_PLAN.slots.json; revision: 2 -->
# Claude DeepSeek Compatibility Validation

## User request

Use DeepSeek as the Claude Code test model to validate Project Governor compatibility and instruction following across both Codex and Claude Code; users should not need to explicitly call /pg-* commands.

## Existing behavior

- Project Governor already ships a Claude Code adapter through `.claude-plugin/plugin.json`, `claude/commands/`, `claude/agents/`, `claude/hooks/`, and `claude/skills/project-governor/SKILL.md`.
- DeepSeek official docs provide Claude Code environment variables for Anthropic-compatible routing; Claude Code official docs support provider-specific model aliases and custom model options.
- The current checkout validates with `claude plugin validate .` before additional testing.

## Existing patterns to reuse

| Pattern | Source file | How it will be reused |
| --- | --- | --- |
| Claude command wrappers | claude/commands/pg-route.md | Validate plugin behavior through the existing `pg-*` command surface instead of adding a DeepSeek-specific command. |
| Claude skill wrapper | claude/skills/project-governor/SKILL.md | Use it as the instruction source for explicit file-read instruction-following tests. |
| Claude compatibility tests | tests/test_claude_code_compat.py | Extend existing structural coverage with automatic governance-context injection assertions. |

## Files expected to change

- Add concise Project Governor context injection on Claude Code `UserPromptSubmit` for natural project-work prompts.
- Clarify the Claude skill wrapper so users should not need to explicitly call `/pg-*` commands for normal governed work.
- Update the target-project `CLAUDE.md` template so initialized projects also tell Claude Code to apply Project Governor automatically.
- Surface `CLAUDE.md` template drift in plugin-upgrade-migrator so already initialized projects such as `ai-tryon` can receive the automatic-entrypoint rule safely.
- Expand tests and task-local validation evidence to cover Codex plugin behavior, Claude plugin behavior, and the `ai-tryon` downstream project fixture without storing secrets.

## Files not to change

- None recorded.

## New files

| File | Why existing files cannot cover it |
| --- | --- |
| tasks/2026-04-30-claude-deepseek-minimum-adapter/TEST_PLAN.md | The research route requires a file-backed test plan for the Claude Code and DeepSeek compatibility validation. |
| tasks/2026-04-30-claude-deepseek-minimum-adapter/QUALITY_REPORT.md | Task-local evidence summarizes commands, findings, and residual risks without changing plugin contracts. |
| tasks/2026-04-30-claude-deepseek-minimum-adapter/SESSION_LEARNING_INPUT.json | Command failures during Claude CLI testing should be recorded in the project-owned command learning ledger without secrets. |

## Dependencies

No new dependencies expected unless explicitly approved.

## Tests

- claude plugin validate .
- claude plugin validate examples/claude-marketplace
- claude -p --bare --model deepseek-v4-flash --output-format json --max-budget-usd 0.02 -- "Respond exactly OK"
- claude -p --bare --plugin-dir . --model deepseek-v4-flash --output-format json --max-budget-usd 0.35 --allowedTools "Bash(python3 *)" -- "/pg-route docs-only README typo fix"
- claude -p --bare --model deepseek-v4-flash --output-format json --max-budget-usd 0.10 --allowedTools "Read" -- "Read AGENTS.md and claude/skills/project-governor/SKILL.md..."
- claude -p --bare --model deepseek-v4-pro --output-format json --max-budget-usd 0.12 --allowedTools "Read" -- "Read AGENTS.md and claude/skills/project-governor/SKILL.md..."
- claude -p --plugin-dir . --strict-mcp-config --mcp-config '{"mcpServers":{}}' --model deepseek-v4-flash --tools "" -- "natural Project Governor prompt..."
- python3 tests/test_claude_code_compat.py
- python3 tests/test_plugin_upgrade_migrator.py
- python3 tests/selftest.py
- python3 -m unittest discover -s tests -p 'test*.py'
- python3 -m compileall tools skills tests claude
- python3 tools/analyze_skill_catalog.py --project . --format text --fail-on-issues
- python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py --project /Users/yxhpy/Desktop/project/ai-tryon --plugin-root /Users/yxhpy/Desktop/project/codex-project-governor
- python3 skills/plugin-upgrade-migrator/scripts/plan_migration.py --project /Users/yxhpy/Desktop/project/ai-tryon --plugin-root /Users/yxhpy/Desktop/project/codex-project-governor --current-version 6.2.5 --target-version 6.2.5
- npm run build in /Users/yxhpy/Desktop/project/ai-tryon
- python3 skills/quality-gate/scripts/run_quality_gate.py /Users/yxhpy/Desktop/project/ai-tryon/tasks/2026-04-30-rbac/quality-gate-input.json
- python3 skills/quality-gate/scripts/run_quality_gate.py /Users/yxhpy/Desktop/project/ai-tryon/tasks/2026-04-30-upload-preview-refresh/quality-gate-input.json

## Risks

- Direct plugin skill invocation in non-interactive DeepSeek sessions produced generic answers unless the relevant files were explicitly read; automatic hook context now reduces reliance on direct skill invocation.
- Low `--max-budget-usd` caps can truncate Claude Code command runs before useful output is emitted; command-wrapper tests now use a higher cap based on observed cost.
- User-level MCP tools can pollute non-interactive Claude smoke tests; strict empty MCP configuration is used for automatic-entrypoint validation.
- Shell environment contains provider credentials; evidence must record only variable names and command shapes, never values.

## Rollback

Revert the Claude hook context injection, Claude skill wording, test additions, and task-local validation artifacts.
