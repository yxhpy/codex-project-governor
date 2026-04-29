# Project Governor 中文使用指南

这份指南面向已经安装 Project Governor 的 Codex 用户，重点说明如何在真实仓库里使用它，而不是解释插件内部实现。

## 基本原则

- 先读项目规则，再改代码。
- 先做迭代计划，再实现非平凡改动。
- 先做任务路由；如果是明确的局部小改，可以走 `micro_patch`，但必须用 `route-guard` 验证实际 diff 没有越界。
- 面向 GPT-5.5 的实现、研究、升级或清理请求，可以先用 `gpt55-auto-orchestrator` 自动选择工作流、模型、上下文预算、subagent 和质量门。
- 已初始化项目优先用 `context-indexer` 查询任务相关章节，先读 `DOCS_MANIFEST.json`、`SESSION_BRIEF.md` 和 `recommended_sections`，避免每个会话都读取所有初始化文档。
- 需要查“为什么当时这样做”或历史决策时，用 `context-indexer --memory-search` 查治理记忆、决策、任务和状态文件，不要拼复杂 shell，也不要默认翻原始聊天记录。
- 非平凡任务自动运行 `subagent-activation`，由项目级 `.codex/agents/` 选择 subagent 和模型策略。
- 对普通功能先做上下文包和模式复用，再走并行实现和质量门。
- 已初始化项目升级 Project Governor 时，使用 `plugin-upgrade-migrator` 先比较新功能并生成安全迁移计划，不要直接覆盖本地治理文件。
- 升级迁移前，如果项目里有插件全局 `.codex` 运行时资产或插件源码目录，先用 `project-hygiene-doctor` 做诊断和安全隔离。
- 需要安装/更新/重装用户级插件或刷新已治理项目时，使用 `clean-reinstall-manager`，先生成计划，再按选择执行。
- 项目采用 `DESIGN.md` 时，先用 `design-md-governor` lint、摘要和 diff，缺失时只给采纳计划，不自动创建。
- 任何 UI/frontend 编码、视觉润色、组件、页面、CSS 或响应式布局改动，先用 `design-md-aesthetic-governor` 检查 Gemini/Stitch 配置，读取 DESIGN.md、生成 read proof，再按 token 实现并做漂移校验。
- Gemini/Stitch 配置可以来自 shell 环境变量，也可以来自项目根目录 `.env-design`；必需键为 `GEMINI_BASE_URL`、`GEMINI_API_KEY`、`GEMINI_MODEL`、`STITCH_MCP_API_KEY`，`GEMINI_PROTOCOL` 可选 `auto`、`openai` 或 `gemini`。通过第三方网关走原生 Gemini 时，`GEMINI_BASE_URL` 必须填该网关的 Gemini 协议根，例如提供 `/gemini/v1beta` 时填 `https://host/gemini`。`STITCH_MCP_URL` 默认是 `https://stitch.googleapis.com/mcp`，`.env-design` 不得提交。
- 默认走托管 Stitch MCP 端点，不需要本地安装 `stitch-mcp`、`npm` 或 `gcloud`；只有项目显式改成本地 MCP server 时才需要安装依赖。
- 如果用户明确要不用 Gemini/Stitch、只用基础模式做前端，可以在 shell 环境变量或项目根 `.env-design` 中设置 `DESIGN_BASIC_MODE=1`；这能避开 Codex hook 或 Windows 进程没有继承后来 shell 变量的问题。
- 先做研究和升级建议，再改 manifest、lockfile、SDK 或工具版本。
- 只把有证据的事实写入项目记忆。
- 初始化已有项目时只写治理文件，不改应用代码。

## 1. 给已有仓库接入治理

适合已经有代码的项目。

```text
Use @project-governor init-existing-project.

Initialize this existing repository for strict iterative development.
Do not modify application code.
Infer conventions from the existing codebase.
Create governance files only.
```

完成后重点检查：

- `AGENTS.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/conventions/ITERATION_CONTRACT.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/memory/OPEN_QUESTIONS.md`
- `tasks/_template/ITERATION_PLAN.md`

## 2. 给新仓库先建治理骨架

适合还没有应用代码的新项目。

```text
Use @project-governor init-empty-project.

Create a Codex-governed project foundation.

Project:
- Name: <项目名>
- Product goal: <产品目标>
- Primary users: <主要用户>
- Preferred stack: <技术栈>

Do not write application code.
Create only governance docs, memory docs, task templates, AGENTS.md, and Codex prompts.
```

## 3. 开始一次功能或修复迭代

当需求不是简单错字修复时，先让 Codex 建立迭代计划：

```text
Use @project-governor iteration-planner.

Request:
<需求内容>

Treat this as an iteration, not a rewrite.
Find adjacent code and reusable patterns first.
Create tasks/<date>-<slug>/ITERATION_PLAN.md.
Do not implement until the plan is complete.
```

计划里至少应该说明：

- 复用哪些已有模式。
- 预计修改哪些文件。
- 哪些文件不应该动。
- 是否新增文件，为什么必须新增。
- 需要跑哪些测试。
- 回滚方式。

## 4. 用质量门加速功能开发

当需求需要更快落地，但仍必须保持质量边界时，先让 `task-router` 选择路线：

```text
Use @project-governor task-router.

Request:
<功能、修复或重构需求>

Choose the fastest safe workflow. Do not implement yet.
Return the route, lane, quality level, change budget, and required downstream skills.
```

典型顺序：

- `subagent-activation`：为 standard、risk、refactor、migration、upgrade、PR review、init 和 broad research 工作流选择 subagent。
- `context-pack-builder`：生成最小上下文包。
- `pattern-reuse-engine`：明确必须复用的现有模式和禁止重复项。
- `test-first-synthesizer`：先规划行为、回归、边界和错误路径覆盖。
- `parallel-feature-builder`：先并行只读分析，再由一个有边界的实现者修改代码。
- `route-guard`：对 `micro_patch`、`tiny_patch` 或 fast-lane 改动验证实际 diff 是否仍符合原路由。
- `quality-gate`：按 `light`、`standard` 或 `strict` 运行质量门。
- `repair-loop`：只在质量门失败时修复，并保持范围有界。
- `merge-readiness`：检查是否可以进入 PR 或 merge。
- `coding-velocity-report`：复盘上下文时间、首次补丁时间、修复轮次和质量分。

确定性脚本入口：

```bash
python3 skills/task-router/scripts/classify_task.py examples/task-router-input.json
python3 skills/task-router/scripts/classify_task.py examples/task-router-micro-input.json
python3 skills/route-guard/scripts/check_route_guard.py examples/route-guard-micro-pass.json
python3 skills/subagent-activation/scripts/select_subagents.py examples/subagent-activation-standard-feature.json
python3 skills/plugin-upgrade-migrator/scripts/compare_features.py --current-version 0.4.1 --target-version 0.4.3 --feature-matrix releases/FEATURE_MATRIX.json
python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py --project /path/to/project --plugin-root /path/to/codex-project-governor
python3 skills/clean-reinstall-manager/scripts/clean_reinstall_orchestrator.py --path . --plugin-root /path/to/codex-project-governor
python3 skills/clean-reinstall-manager/scripts/apply_latest_runtime_mode.py --path . --plugin-root /path/to/codex-project-governor --apply
python3 skills/design-md-governor/scripts/lint_design_md.py DESIGN.md
python3 skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py examples/gpt55-runtime-standard-feature.json
python3 skills/context-indexer/scripts/build_context_index.py --project . --write
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "dashboard widget"
python3 skills/session-lifecycle/scripts/session_lifecycle.py start --project . --task-id demo --route standard_feature
python3 skills/evidence-manifest/scripts/write_evidence_manifest.py --project . --task-id demo --route standard_feature --validate
python3 skills/harness-doctor/scripts/doctor.py --project . --execution-readiness
python3 skills/context-pack-builder/scripts/build_context_pack.py . --request "dashboard widget"
python3 skills/pattern-reuse-engine/scripts/find_reuse_candidates.py . --request "dashboard widget"
python3 skills/quality-gate/scripts/run_quality_gate.py examples/quality-gate-input.json
python3 skills/merge-readiness/scripts/check_merge_readiness.py examples/merge-readiness-input.json
python3 skills/coding-velocity-report/scripts/build_velocity_report.py examples/velocity-input.json
python3 skills/memory-compact/scripts/record_session_learning.py --project . --input /path/to/session-learning.json
```

## 5. 使用 Harness v6.0.6、GPT-5.5 自动编排和上下文索引

v6.0.6 起，Project Governor 作为 Harness 工作：`task-router` 是 route、risk、confidence、guardrail、route doc pack 和 evidence requirement 的唯一真源；`gpt55-auto-orchestrator` 在这个结果上做运行时规划；`context-indexer` 会生成 `DOCS_MANIFEST.json` 并返回章节级 line range；UI 工作额外经过 DESIGN.md gate，历史问题、失败命令和过期记忆候选可通过 `context-indexer --memory-search` 查询；插件升级会暴露 `AGENTS.md` 规则模板漂移；本地 marketplace 安装可用 Git helper 更新插件 checkout。它不会为微补丁强制使用重模型，也不会跳过 `route-guard`、session learning 和质量门。

```text
Use @project-governor gpt55-auto-orchestrator.

Automatically choose the Project Governor workflow, models, context budget, subagents, and quality gates for this request.
Do not ask the user to name skills or subagents.
Read DOCS_MANIFEST, then query section-level context before reading large initialization docs.
```

`context-indexer` 会把项目上下文写入项目自有的 `.project-governor/context/`，用于后续任务检索：

```bash
python3 skills/context-indexer/scripts/build_context_index.py --project . --write
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "dashboard widget"
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "为什么当时选择这个 checkout 流程" --memory-search --auto-build
```

`build_context_index.py --write` 会生成 `.project-governor/context/DOCS_MANIFEST.json`。`query_context_index.py` 会返回 `recommended_sections`、`must_read_sections`、`progressive_read_plan` 和 `avoid_docs`；默认排除标记为 `stale` 或 `superseded` 的文档，只有历史、清理或迁移审查任务才使用 `--include-stale`。

`--memory-search` 会把检索范围收窄到受治理的历史资产，例如 `docs/memory/`、`docs/decisions/`、`tasks/`、发布记录和 `.project-governor/state/`。需要给人读的结果时可加 `--format text`。

非平凡 session 开始时，应先查相关失败命令、重复错误和过期记忆；session 结束前，如果出现命令失败、假设被纠正或发现记忆过期，应记录 session learning：

```bash
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "<任务请求> command failures repeated mistakes stale memory" --memory-search --auto-build --format text
python3 skills/memory-compact/scripts/record_session_learning.py --project . --input /path/to/session-learning.json --apply
```

记录规则：

- 一次性失败命令进入 `.project-governor/state/COMMAND_LEARNINGS.json`。
- 重复错误进入 `docs/memory/REPEATED_AGENT_MISTAKES.md`，同时保留命令学习 ledger。
- 失效、被取代或导致膨胀的记忆进入 `.project-governor/state/MEMORY_HYGIENE.json`，等待标记 superseded 或清理。
- 这些 state 文件会被 `--memory-search` 检索到，所以新 session 不需要用户再次提醒“记一下”。

Harness v6 的项目状态和证据入口：

```bash
python3 skills/session-lifecycle/scripts/session_lifecycle.py start --project . --task-id demo --route standard_feature
python3 skills/evidence-manifest/scripts/write_evidence_manifest.py --project . --task-id demo --route standard_feature --validate
python3 skills/harness-doctor/scripts/doctor.py --project . --execution-readiness
```

需要把最新运行模式写入已治理项目时，使用：

```bash
python3 skills/clean-reinstall-manager/scripts/apply_latest_runtime_mode.py \
  --path . \
  --plugin-root /path/to/codex-project-governor \
  --apply
```

## 6. 治理 DESIGN.md 设计系统

v0.4.7 起，`design-md-governor` 可以把项目自己的 `DESIGN.md` 作为 UI/视觉实现前的设计系统真源。它不会自动创建或覆盖 `DESIGN.md`；缺失时只给采纳计划，除非用户明确选择创建。

```text
Use @project-governor design-md-governor.

Detect whether DESIGN.md exists.
Lint and summarize it if present.
Recommend an adoption plan if missing.
Do not create or overwrite DESIGN.md unless the user explicitly opts in.
```

常用脚本：

```bash
python3 skills/design-md-governor/scripts/lint_design_md.py DESIGN.md
python3 skills/design-md-governor/scripts/summarize_design_md.py DESIGN.md
python3 skills/design-md-governor/scripts/diff_design_md.py DESIGN.before.md DESIGN.md
```

## 7. 实现前研究候选能力

当你想引入新的治理规则、agent 模式、hook、skill、库或自动化方式时，先使用 `research-radar`。

```text
Use @project-governor research-radar.

Research this candidate before implementation:
<候选能力或方案>

Advisory only.
Prefer official docs, changelogs, release notes, and project docs.
Show source quality, matched project needs, risk, maturity, recommendation, and user choices.
Do not modify code or manifests.
```

输出建议应落在这些类别之一：

- `adopt_now`：证据强、风险低、直接匹配当前需求。
- `spike`：有价值但风险或不确定性较高，应该隔离验证。
- `watch`：暂时观察，当前不实现。
- `reject`：不符合项目方向或风险超过收益。

如果已经有结构化候选清单，可以运行：

```bash
python3 skills/research-radar/scripts/score_research_candidates.py \
  --manifest examples/research-candidates.json \
  --need memory \
  --need subagents \
  --need research
```

## 8. 升级前研究版本

当涉及依赖、工具、SDK、运行时或 Project Governor 自身版本变化时，先用 `version-researcher`。

```text
Use @project-governor version-researcher.

Research candidate versions before upgrade-advisor is used.
Show current version, candidate versions, skipped versions, evidence quality, relevant changes, migration risk, request match, and recommendation.
Do not modify manifests, lockfiles, application code, CI config, hooks, or rules.
```

结构化版本研究示例：

```bash
python3 skills/version-researcher/scripts/research_versions.py \
  --manifest examples/version-research-manifest.json \
  --request "Need better memory and subagent governance"
```

## 9. 升级前给出用户可选路径

`upgrade-advisor` 不直接升级，而是输出菜单和理由。

```text
Use @project-governor upgrade-advisor.

Request:
<当前需求>

Advisory only. Do not edit manifests or install packages.
Show which dependencies or tools are behind, relevant, risky, optional, deferred, or should be pinned.
```

常见选择：

- `upgrade_now`
- `plan_upgrade_iteration`
- `defer`
- `reject_or_pin`

只有用户明确选择后，才进入实际升级迭代。

## 10. 检查项目卫生

v0.4.4 起，初始化默认使用 clean profile：复制 `AGENTS.md`、`docs/`、`tasks/_template/`、`.project-governor/`、`.codex/rules/`、`.codex/hooks/` 和 `.codex/hooks.json` 等项目治理文件。插件全局 `.codex/agents`、`.codex/prompts` 和 `.codex/config.toml` 默认留在插件安装目录。

```bash
python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py \
  --project /path/to/project \
  --plugin-root /path/to/codex-project-governor
```

如果报告里只有安全的生成型全局资产，可以隔离而不是删除：

```bash
python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py \
  --project /path/to/project \
  --plugin-root /path/to/codex-project-governor \
  --apply
```

如果项目确实需要旧式 `.codex` 运行时资产，可在初始化时显式使用：

```bash
python3 tools/init_project.py --mode existing --profile legacy-full --target /path/to/repo
```

## 11. 干净重装或刷新治理项目

v6.0.6 起，`tools/install_or_update_user_plugin.py` 可以安装或更新用户级插件 checkout，并确保本地 marketplace entry 指向该 checkout。`clean-reinstall-manager` 仍负责生成用户级重装命令、从项目外发现已治理仓库，并在项目内刷新缺失的项目治理模板。它默认把插件全局噪音隔离到 `.project-governor/trash/<timestamp>/`，不会直接删除。

```text
Use @project-governor clean-reinstall-manager.

Cleanly reinstall the user-level Project Governor plugin and refresh initialized projects without polluting project directories.
```

常用脚本：

```bash
python3 tools/install_or_update_user_plugin.py --ref v6.0.6 --apply
python3 skills/clean-reinstall-manager/scripts/generate_reinstall_instructions.py --ref v6.0.6
python3 skills/clean-reinstall-manager/scripts/discover_governed_projects.py --root "$HOME"
python3 skills/clean-reinstall-manager/scripts/refresh_project_governance.py --project . --plugin-root /path/to/codex-project-governor
python3 skills/clean-reinstall-manager/scripts/clean_reinstall_orchestrator.py --path . --plugin-root /path/to/codex-project-governor
```

如果当前目录不是 Project Governor 项目，orchestrator 会停止并列出发现的项目，不会修改当前目录。

## 11. 压缩项目记忆

适合阶段性维护、长会话后整理、发布后复盘。

```text
Use @project-governor memory-compact.

Compact project memory from the last 7 days.
Read recent task retros, execution logs, docs changes, PR feedback, and repeated mistakes.
Update only docs/memory/, docs/decisions/, and AGENTS.md when justified by evidence.
Do not modify application code.
```

分类规则：

- 确认事实写入 `docs/memory/PROJECT_MEMORY.md`。
- 不确定事项写入 `docs/memory/OPEN_QUESTIONS.md`。
- 重复错误写入 `docs/memory/REPEATED_AGENT_MISTAKES.md`。
- 风险写入 `docs/memory/RISK_REGISTER.md`。
- 架构或产品决策写入 `docs/decisions/ADR-*.md` 或 `PDR-*.md`。

## 12. PR 或分支治理审查

```text
Use @project-governor pr-governance-review.

Review this branch against main.
Check iteration compliance, style drift, architecture drift, tests, dependency risk, and docs/memory needs.
Return blockers, warnings, and required patches.
```

审查重点：

- 是否偏离迭代计划。
- 是否新增未批准依赖。
- 是否引入新架构或目录模式。
- 是否遗漏测试和文档更新。
- 是否需要把重复问题沉淀进 memory 或 AGENTS.md。

## 12. 发布前检查

发布插件变更前建议执行：

```bash
python3 tests/selftest.py
python3 -m compileall tools skills tests
python3 tools/init_project.py --mode existing --target /tmp/project-governor-smoke --json
python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py --project /tmp/project-governor-smoke --plugin-root .
```

如果改了模板、skill、helper 输出或 manifest，必须同步更新：

- `README.md`
- `README.zh-CN.md`
- `tests/selftest.py`
- 相关 `templates/` 文件
- 相关 `docs/` 或任务计划

## 13. 常见误区

- 不要把 Project Governor 当应用框架；它是治理插件和模板包。
- 不要在初始化已有项目时顺手修改应用代码。
- 不要没有 ADR/PDR 就新增依赖或运行时层。
- 不要把推测写入 durable memory。
- 不要在用户选择升级路径前修改 manifest 或 lockfile。
- 不要为了速度跳过 `quality-gate`，也不要让多个写代理修改重叠生产代码。
- 不要把一次小修复扩大成重构或重写。
