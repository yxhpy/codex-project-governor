# Test Plan: Codex and Claude Compatibility Validation

## Behavior To Protect

- Codex plugin metadata, skills, prompts, initialization templates, and deterministic governance scripts remain valid.
- Claude Code can load the Project Governor plugin from this checkout.
- DeepSeek V4 Pro and Flash can be used as Claude Code test models through the current Anthropic-compatible environment.
- Natural Codex and Claude Code project requests should enter Project Governor automatically; explicit `/pg-*` commands are optional diagnostics.
- Initialized projects receive a `CLAUDE.md` that preserves `@AGENTS.md` and does not require visible `/pg-*` command invocation.
- Existing initialized projects surface `CLAUDE.md` template drift through the upgrade migrator.
- Model instruction-following is judged against repository files, not generic memory.

## Test Matrix

| Case | Required? | Test / Command | Notes |
|---|---|---|---|
| Codex manifest and default prompts | Yes | `python3 tests/selftest.py` | Validates `.codex-plugin/plugin.json`, default prompts, required templates, and init behavior. |
| Codex full deterministic suite | Yes | `python3 -m unittest discover -s tests -p "test*.py"` | Covers routing, context index, quality gate helpers, execution policy, upgrades, hygiene, session learning, user installer, design gates, and Claude compat tests. |
| Codex syntax/import surface | Yes | `python3 -m compileall tools skills tests claude` | Guards Python syntax across deterministic helpers and tests. |
| Codex plugin structure | Yes | `python3 tools/analyze_skill_catalog.py --project . --format text --fail-on-issues` | Validates skill catalog grouping and README skill sections. |
| Codex initialized project template | Yes | `python3 tools/init_project.py --mode existing --target <tmpdir> --json` plus tests | Confirms clean profile copies `AGENTS.md`, automatic `CLAUDE.md`, project hooks, runtime state, and no application code. |
| Codex CLI natural prompt, plugin repo | Yes | `codex --ask-for-approval never exec --cd <plugin-root> --sandbox read-only --ephemeral --json ...` | Confirms real Codex CLI returns `auto_project_governor=true` and `explicit_skill_required=false` without modifying files. |
| Codex CLI natural prompt, downstream project | Yes | `codex --ask-for-approval never exec --cd /Users/yxhpy/Desktop/project/ai-tryon --sandbox read-only --ephemeral --json ...` | Confirms initialized app projects also enter Project Governor automatically in Codex CLI. |
| Claude manifest and adapter paths | Yes | `claude plugin validate .` | Validates `.claude-plugin`, commands, agents, hooks, skills, and MCP wiring. |
| Claude marketplace package | Yes | `claude plugin validate examples/claude-marketplace` | Validates distribution example. |
| Claude automatic hook context | Yes | `python3 tests/test_claude_code_compat.py` | Covers English and Chinese natural governance prompts plus UI context injection. |
| Claude skill and template contract | Yes | `python3 tests/test_claude_code_compat.py` | Ensures skill and generated `CLAUDE.md` say users do not need explicit `/pg-*`. |
| Claude upgrade drift | Yes | `python3 tests/test_plugin_upgrade_migrator.py` | Ensures old `CLAUDE.md` templates are surfaced for safe migration. |
| Claude DeepSeek Flash smoke | Yes | `claude -p --bare --model deepseek-v4-flash --output-format json --max-budget-usd 0.02 -- "Respond exactly OK"` | Confirms the fast test model works in Claude Code. |
| Claude DeepSeek Flash command wrapper | Yes | `claude -p --bare --plugin-dir . --model deepseek-v4-flash ... "/pg-route docs-only README typo fix"` | Confirms optional diagnostic command path still works. |
| Claude DeepSeek Flash natural project prompt | Yes | `claude -p --plugin-dir . --model deepseek-v4-flash ...` | Confirms natural prompt reports `explicit_pg_required: false` and starts with AGENTS/CLAUDE plus task-router/context-indexer. |
| Claude DeepSeek Pro instruction following | Yes | `claude -p --bare --model deepseek-v4-pro --allowedTools "Read" ...` | Confirms high-capability model reads repo files and follows Project Governor instructions. |
| Actual project hygiene | Yes | `inspect_project_hygiene.py --project /Users/yxhpy/Desktop/project/ai-tryon` | Confirms the governed app project is a clean-profile target, not a plugin-source leak. |
| Actual project Codex checks | Yes | `npm run build`, selected quality gate inputs, context-index query | Confirms `ai-tryon` remains usable as a real governed project fixture. |
| Actual project Claude checks | Yes | Hook and Claude CLI natural prompt from `ai-tryon` cwd with `--plugin-dir <plugin-root>` | Confirms Claude works from a downstream initialized project without visible `/pg-*` commands. |
| Diff hygiene | Yes | `git diff --check` | Guards whitespace errors in the plugin patch. |
| Engineering standards | Yes | `check_engineering_standards.py --project . --scope diff --diff-base HEAD` | Diff scope must have no blockers. Baseline full-scope warnings are recorded separately if present. |
| Quality gate | Yes | `run_quality_gate.py <task QUALITY_GATE_INPUT.json>` | Final Project Governor gate for this task evidence. |

## Existing Tests To Reuse

- `tests/test_claude_code_compat.py`
- `tests/selftest.py`
- `tests/test_plugin_upgrade_migrator.py`
- Full `unittest discover` suite under `tests/`

## New Or Updated Tests

- `tests/test_claude_code_compat.py` now covers Chinese/English natural prompt auto-context, UI context composition, automatic `CLAUDE.md` template wording, and initialized-project output.
- `tests/test_plugin_upgrade_migrator.py` now covers `CLAUDE.md` rule-template drift.
- `tests/selftest.py` now checks initialized `CLAUDE.md` does not require explicit `/pg-route`.

## Mock Governance

| Mock / Fixture | Real dependency or contract | Guarding integration/contract/smoke test |
|---|---|---|
| None | Claude Code CLI and configured DeepSeek-compatible endpoint | `claude -p` model and plugin command smoke tests |

## Commands

- `claude plugin validate .`
- `claude plugin validate examples/claude-marketplace`
- `claude -p --bare --model deepseek-v4-flash --output-format json --max-budget-usd 0.02 -- "Respond exactly OK"`
- `claude -p --bare --plugin-dir . --model deepseek-v4-flash --output-format json --max-budget-usd 0.08 --allowedTools "Bash(python3 *)" -- "/pg-route docs-only README typo fix"`
- `claude -p --bare --model deepseek-v4-flash --output-format json --max-budget-usd 0.10 --allowedTools "Read" -- "Read AGENTS.md and claude/skills/project-governor/SKILL.md..."`
- `claude -p --bare --model deepseek-v4-pro --output-format json --max-budget-usd 0.12 --allowedTools "Read" -- "Read AGENTS.md and claude/skills/project-governor/SKILL.md..."`
- `python3 tests/test_claude_code_compat.py`
- `python3 tests/test_plugin_upgrade_migrator.py`
- `python3 tests/selftest.py`
- `python3 -m unittest discover -s tests -p "test*.py"`
- `python3 -m compileall tools skills tests claude`
- `python3 tools/analyze_skill_catalog.py --project . --format text --fail-on-issues`
- `codex --ask-for-approval never exec --cd /Users/yxhpy/Desktop/project/codex-project-governor --sandbox read-only --ephemeral --json "..."`
- `codex --ask-for-approval never exec --cd /Users/yxhpy/Desktop/project/ai-tryon --sandbox read-only --ephemeral --json "..."`
- `python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --scope diff --diff-base HEAD`
- `git diff --check`
- `python3 skills/quality-gate/scripts/run_quality_gate.py tasks/2026-04-30-claude-deepseek-minimum-adapter/QUALITY_GATE_INPUT.json`

Do not delete or weaken tests to pass.
