# Quality Report: Codex and Claude Compatibility Validation

## Status

- Result: Pass
- Gate level: Standard compatibility validation
- Route: research

## Checks

| Check | Status | Evidence |
|---|---|---|
| Codex full deterministic suite | Pass | `python3 -m unittest discover -s tests -p 'test*.py'` ran 104 tests, all passed. |
| Codex selftest | Pass | `python3 tests/selftest.py` ran 16 tests, all passed, including initialized `CLAUDE.md` automatic-entrypoint assertions. |
| Codex skill catalog | Pass | `python3 tools/analyze_skill_catalog.py --project . --format text --fail-on-issues` passed with 35 skills and no consolidation candidates. |
| Codex CLI natural prompt, plugin repo | Pass | `codex --ask-for-approval never exec --cd /Users/yxhpy/Desktop/project/codex-project-governor --sandbox read-only --ephemeral --json ...` returned `auto_project_governor:true`, `explicit_skill_required:false`. |
| Codex CLI natural prompt, ai-tryon | Pass | `codex --ask-for-approval never exec --cd /Users/yxhpy/Desktop/project/ai-tryon --sandbox read-only --ephemeral --json ...` returned `auto_project_governor:true`, `explicit_skill_required:false`. |
| Python syntax/import surface | Pass | `python3 -m compileall tools skills tests claude` passed. |
| Diff hygiene | Pass | `git diff --check` passed. |
| Diff engineering standards | Pass | Diff scope scanned 5 files, 0 blockers, 0 warnings. |
| Claude plugin manifest | Pass | `claude plugin validate .` passed. |
| Claude marketplace manifest | Pass | `claude plugin validate examples/claude-marketplace` passed. |
| DeepSeek Flash model smoke | Pass | `claude -p --bare --model deepseek-v4-flash ...` returned `OK`. |
| Project Governor command wrapper | Pass | `/pg-route docs-only README typo fix` classified `docs_only`, `fast_lane`, quality `light` after raising the test budget cap to $0.35. |
| Automatic Project Governor context | Pass | Claude hook injects Project Governor guidance on English and Chinese natural project-work prompts without requiring `/pg-*`; UI prompts also get DESIGN.md context. |
| DeepSeek natural prompt auto-entrypoint smoke | Pass | With strict empty MCP config, DeepSeek Flash returned `auto_project_governor: true`, `explicit_pg_required: false`, and no permission denials. |
| Explicit file-based instruction following, Flash | Pass | Flash read `AGENTS.md` and `claude/skills/project-governor/SKILL.md`, then returned the project identity, required reading, and forbidden defaults from repo files. |
| Explicit file-based instruction following, Pro | Pass | Pro read the same files and returned concise Project Governor-specific first steps. |
| Claude initialized project template | Pass | `templates/CLAUDE.md`, `tests/test_claude_code_compat.py`, and `tests/selftest.py` verify automatic invocation and no explicit `/pg-route` requirement. |
| Claude upgrade drift | Pass | `tests/test_plugin_upgrade_migrator.py` verifies `CLAUDE.md` rule-template drift; `ai-tryon` plan reports one safe `CLAUDE.md` update operation. |
| `ai-tryon` project hygiene | Pass | `inspect_project_hygiene.py` reports `status: clean`, 0 safe-to-quarantine, 0 manual-review findings. |
| `ai-tryon` build | Pass | `npm run build` passed in `/Users/yxhpy/Desktop/project/ai-tryon`. |
| `ai-tryon` task gates | Pass | RBAC strict gate and upload-preview standard gate both passed with 0 blockers, 0 warnings. |
| `ai-tryon` Claude natural prompt | Pass | Claude CLI from `ai-tryon` cwd returned `auto_project_governor: true`, `explicit_pg_required: false`, no permission denials. |
| Secrets hygiene | Pass | Evidence records command shapes and variable names only; provider credential values are not stored. |
| Durable memory | Pass | `docs/memory/PROJECT_MEMORY.md` records the confirmed Claude automatic-entrypoint behavior with evidence. |
| Existing Claude compat tests | Pass | `python3 tests/test_claude_code_compat.py` ran 9 tests, all passed. |
| Upgrade migrator tests | Pass | `python3 tests/test_plugin_upgrade_migrator.py` ran 13 tests, all passed. |
| Session learning | Pass | `record_session_learning.py --apply` recorded/updated four command learnings in `.project-governor/state/COMMAND_LEARNINGS.json`. |

## Blocking Issues

- None for the defined Codex, Claude Code, DeepSeek, and `ai-tryon` compatibility matrix.

## Warnings

- Direct skill invocation is not used as the acceptance path in non-interactive DeepSeek tests; the accepted paths are hook context, explicit file reads, and optional `pg-*` diagnostics.
- `--tools` is variadic; use `--` before the prompt when passing an empty tool list.
- Use `--strict-mcp-config --mcp-config '{"mcpServers":{}}'` for deterministic Claude smoke tests so user-level MCP tools do not pollute the scenario.
- `ai-tryon` remains a dirty real-world fixture with known historical governance debt; this task validates it as a regression target, not as a fully PR-ready app baseline.

## Commands Run

- `claude plugin validate .`
- `claude plugin validate examples/claude-marketplace`
- `claude -p --bare --model deepseek-v4-flash --output-format json --max-budget-usd 0.02 -- "Respond exactly OK"`
- `claude -p --bare --plugin-dir . --model deepseek-v4-flash --output-format json --max-budget-usd 0.35 --allowedTools "Bash(python3 *)" -- "/pg-route docs-only README typo fix"`
- `claude -p --bare --model deepseek-v4-flash --output-format json --max-budget-usd 0.10 --allowedTools "Read" -- "Read AGENTS.md and claude/skills/project-governor/SKILL.md..."`
- `claude -p --bare --model deepseek-v4-pro --output-format json --max-budget-usd 0.12 --allowedTools "Read" -- "Read AGENTS.md and claude/skills/project-governor/SKILL.md..."`
- `claude -p --plugin-dir . --strict-mcp-config --mcp-config '{"mcpServers":{}}' --model deepseek-v4-flash --output-format json --max-budget-usd 0.35 --tools "" -- "natural Project Governor prompt..."`
- `python3 tests/test_claude_code_compat.py`
- `python3 tests/test_plugin_upgrade_migrator.py`
- `python3 tests/selftest.py`
- `python3 -m unittest discover -s tests -p 'test*.py'`
- `python3 -m compileall tools skills tests claude`
- `python3 tools/analyze_skill_catalog.py --project . --format text --fail-on-issues`
- `codex --ask-for-approval never exec --cd /Users/yxhpy/Desktop/project/codex-project-governor --sandbox read-only --ephemeral --json "..."`
- `codex --ask-for-approval never exec --cd /Users/yxhpy/Desktop/project/ai-tryon --sandbox read-only --ephemeral --json "..."`
- `python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --scope diff --diff-base HEAD`
- `git diff --check`
- `python3 skills/memory-compact/scripts/record_session_learning.py --project . --input tasks/2026-04-30-claude-deepseek-minimum-adapter/SESSION_LEARNING_INPUT.json --apply`
- `python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py --project /Users/yxhpy/Desktop/project/ai-tryon --plugin-root /Users/yxhpy/Desktop/project/codex-project-governor`
- `python3 skills/plugin-upgrade-migrator/scripts/plan_migration.py --project /Users/yxhpy/Desktop/project/ai-tryon --plugin-root /Users/yxhpy/Desktop/project/codex-project-governor --current-version 6.2.5 --target-version 6.2.5`
- `python3 skills/context-indexer/scripts/query_context_index.py --project /Users/yxhpy/Desktop/project/ai-tryon --request "Claude Code automatic Project Governor no explicit pg command Codex governed project" --memory-search --auto-build --format text`
- `npm run build` in `/Users/yxhpy/Desktop/project/ai-tryon`
- `python3 skills/quality-gate/scripts/run_quality_gate.py /Users/yxhpy/Desktop/project/ai-tryon/tasks/2026-04-30-rbac/quality-gate-input.json`
- `python3 skills/quality-gate/scripts/run_quality_gate.py /Users/yxhpy/Desktop/project/ai-tryon/tasks/2026-04-30-upload-preview-refresh/quality-gate-input.json`
- Claude hook direct smoke from `/Users/yxhpy/Desktop/project/ai-tryon`
- Claude CLI natural prompt from `/Users/yxhpy/Desktop/project/ai-tryon` with strict empty MCP config

## Repair-Loop Input

- Repaired during validation:
  - Raised `/pg-route` Claude smoke budget from `$0.12` to `$0.35`.
  - Added strict empty MCP config for deterministic natural-prompt tests.
  - Strengthened hook context to prefer local files/scripts and avoid unrelated web/browser/MCP tools.
