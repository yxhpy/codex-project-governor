# codex-project-governor

中文 | [English](README.md)

`codex-project-governor` 是一个 Codex 和 Claude Code 插件，用来把仓库变成可自我治理的 Agent 项目。它会把项目规则、约定、决策、风险、记忆、迭代计划和检查入口放进版本控制，让后续 Codex 或 Claude Code 会话能按同一套规则继续工作，而不是每次重新摸索。

当前版本：`6.2.0`

## 它解决什么问题

普通仓库在长期使用 Codex 时容易出现这些问题：

- 新会话忘记项目规则和历史决策。
- 小改动被做成重写。
- 风格、架构、组件和 API 契约逐渐漂移。
- 升级依赖、工具或 SDK 前缺少证据和风险分级。
- 有用经验只留在聊天记录里，没有进入仓库。

Project Governor 的做法是把治理资产放在仓库内：

- `AGENTS.md`：项目级行为规则。
- `CLAUDE.md`：Claude Code 项目入口，默认导入 `AGENTS.md`。
- `docs/conventions/`：代码、架构、UI、组件、迭代约定。
- `docs/memory/`：可追溯的项目记忆、风险和常见错误。
- `docs/decisions/`：ADR/PDR 决策记录。
- `docs/upgrades/`：升级策略、升级登记和发布研究。
- `docs/research/`：候选能力研究、证据质量和采纳建议。
- `tasks/`：每次迭代的计划、日志和复盘。
- `skills/`：可复用的 Codex 工作流。
- `claude/`：Claude Code 的 skill、slash command、subagent 和 hook 适配层。
- `templates/`：初始化目标仓库时复制的治理模板。
- `managed-assets/`：插件自有的可选资产，不默认复制到目标项目。

## 核心能力

- 初始化空仓库或已有仓库，只写治理文件，不改应用代码。
- 挖掘已有仓库的技术栈、目录结构、测试、样式和约定。
- 强制非平凡改动先做迭代计划，避免重写式开发。
- 检查实现风险、样式漂移、架构漂移和 PR 治理问题。
- 在升级前进行版本距离、跳过版本、风险和需求相关性分析。
- 在实现新能力前做研究雷达，判断 `adopt_now`、`spike`、`watch` 或 `reject`。
- 用 Harness v6.2.0、任务路由、微补丁路由、route guard、GPT-5.5 运行时规划、上下文索引 v2、`DOCS_MANIFEST.json`、章节级检索、路线级文档包、治理记忆搜索、会话学习 ledger、会话状态、证据清单、自动 subagent 激活、工程规范扫描、插件升级迁移器、AGENTS.md/CLAUDE.md 规则模板漂移检测、Claude Code commands/agents/hooks、本地 marketplace 的用户级 Git 安装/更新、项目卫生检查、干净重装管理、DESIGN.md 治理、DESIGN.md UI 编码门、上下文包、模式复用、并行实现、质量门、修复循环和合并就绪检查，把提速约束在质量边界内。
- 把近期任务、复盘和重复错误压缩成可审计的项目记忆。
- 提供无第三方依赖的 Python helper 脚本和 self-test。

## 技能列表

| Skill | 用途 |
|---|---|
| `init-empty-project` | 为新仓库创建治理骨架，不写应用代码。 |
| `init-existing-project` | 为已有仓库创建治理层，并从现有代码中归纳约定。 |
| `convention-miner` | 只读扫描仓库，识别栈、目录、测试、API 和组件线索。 |
| `iteration-planner` | 把需求拆成一次迭代，先计划再实现。 |
| `implementation-guard` | 检测重写风险、未批准依赖、新文件缺少说明和公共契约漂移。 |
| `style-drift-check` | 检测组件、设计 token、命名和视觉风格漂移。 |
| `architecture-drift-check` | 检测模块边界、导入方向和契约漂移。 |
| `pr-governance-review` | 用多维度审查方式做 PR 治理 review。 |
| `memory-compact` | 把近期活动压缩成项目记忆、风险和待确认问题。 |
| `release-retro` | 把发布经验转成复盘、记忆和决策记录。 |
| `upgrade-advisor` | 升级前给出版本距离、需求相关性、风险和用户可选路径。 |
| `plugin-upgrade-migrator` | 比较 Project Governor 版本差异，规划安全迁移，并避免覆盖已初始化项目的本地定制。 |
| `project-hygiene-doctor` | 检测被复制到目标项目里的插件全局资产，并隔离安全的生成型 `.codex` 运行时文件。 |
| `clean-reinstall-manager` | 生成用户级插件安装/重装指令，发现已治理项目，并在不复制插件全局资产的前提下刷新项目治理文件。 |
| `design-md-governor` | 把 Google Labs Code DESIGN.md 作为可选设计系统真源，支持 lint、摘要、diff 和迁移建议，但不自动创建项目设计文件。 |
| `design-md-aesthetic-governor` | 在 UI/frontend 编码前强制检查 Gemini/Stitch 配置、读取 DESIGN.md、生成 read proof、选择审美参考、按 token 实现并校验漂移。 |
| `version-researcher` | 在 upgrade-advisor 前研究候选版本、跳过版本、证据质量和迁移风险。 |
| `research-radar` | 在实现新能力前研究候选方案、证据质量、项目匹配度和风险。 |
| `task-router` | 把需求分流到最快且安全的 Project Governor 工作流、通道、质量等级和变更预算。 |
| `route-guard` | 验证实际 diff 是否仍符合 task-router 选定的路由，尤其是 `micro_patch` 和 fast-lane 改动。 |
| `subagent-activation` | 按 route、workflow、风险、质量等级和置信度选择项目级 subagent 与模型策略，避免用户手动列 subagent。 |
| `gpt55-auto-orchestrator` | 面向 GPT-5.5 自动选择工作流、模型计划、上下文预算、subagent 和质量门。 |
| `context-indexer` | 构建 `CONTEXT_INDEX.json`、`DOCS_MANIFEST.json`、章节级检索和治理记忆/历史搜索，避免每个会话都读取所有初始化文档。 |
| `context-pack-builder` | 构建带章节行号、token 预算和压缩策略的最小任务上下文包，减少 Codex 和子代理重复探索仓库。 |
| `session-lifecycle` | 启动和结束 Harness v6 任务会话，并维护 `.project-governor/state` 项目状态。 |
| `evidence-manifest` | 创建或校验任务证据清单，把验收标准、测试、审查和文档刷新决策关联起来。 |
| `harness-doctor` | 诊断 Harness v6 安装结构、上下文新鲜度、状态文件、必需技能和执行就绪度。 |
| `pattern-reuse-engine` | 找出现有组件、服务、hook、schema、测试和样式模式，避免重复造新模式。 |
| `parallel-feature-builder` | 用质量门约束的子代理流水线实现功能：先只读分析，再单一实现者，再测试、审查和修复。 |
| `test-first-synthesizer` | 按现有测试风格先产出目标测试计划或测试骨架。 |
| `engineering-standards-governor` | 在质量门前检查文件规模、函数复杂度、生产 mock 泄漏、测试断言、边界测试计划和复用优先合规性。 |
| `quality-gate` | 运行分层质量检查，覆盖迭代合规、漂移、变更预算、测试、文档和记忆更新。 |
| `repair-loop` | 在质量门失败时执行有边界的修复循环，不删除测试、不削弱断言、不扩大范围。 |
| `merge-readiness` | 检查任务或分支是否 PR-ready，覆盖 blocker、质量门、文档、记忆、测试、预算和审批。 |
| `coding-velocity-report` | 记录上下文时间、首次补丁时间、修复轮次、质量门通过率、补丁规模和复用比例。 |

## 安装到个人 Codex

用安装/更新脚本克隆插件，并写入本地 marketplace entry：

```bash
curl -fsSL https://raw.githubusercontent.com/yxhpy/codex-project-governor/main/tools/install_or_update_user_plugin.py \
  -o /tmp/install_or_update_user_plugin.py
python3 /tmp/install_or_update_user_plugin.py --ref v6.2.0 --apply
```

生成的 `~/.agents/plugins/marketplace.json` 仍然是本地 marketplace 指针：

```json
{
  "name": "personal-codex-plugins",
  "interface": {
    "displayName": "Personal Codex Plugins"
  },
  "plugins": [
    {
      "name": "codex-project-governor",
      "source": {
        "source": "local",
        "path": "./.codex/plugins/codex-project-governor"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Developer Tools"
    }
  ]
}
```

重启 Codex，打开 `/plugins`，选择个人 marketplace，然后安装 **Project Governor**。

### 升级本地 marketplace 安装

上面的 entry 在 Codex 看来是 `source: local`，所以内置 Git marketplace upgrade 不会拉取这个插件 checkout。需要直接更新 Git checkout，然后重启 Codex：

```bash
curl -fsSL https://raw.githubusercontent.com/yxhpy/codex-project-governor/main/tools/install_or_update_user_plugin.py \
  -o /tmp/install_or_update_user_plugin.py
python3 /tmp/install_or_update_user_plugin.py --ref v6.2.0 --apply
```

安装到 v6.2.0 后，同一个 helper 也可以直接从插件 checkout 运行：

```bash
python3 ~/.codex/plugins/codex-project-governor/tools/install_or_update_user_plugin.py --ref v6.2.0 --apply
```

当旧版本还没有这个 helper 时，也可以用等价的手工命令：

```bash
PLUGIN_DIR="${CODEX_PROJECT_GOVERNOR_PLUGIN_DIR:-$HOME/.codex/plugins/codex-project-governor}"
git -C "$PLUGIN_DIR" fetch --tags origin
git -C "$PLUGIN_DIR" checkout --detach v6.2.0
python3 "$PLUGIN_DIR/tests/selftest.py"
```

更新插件本体后，再在已初始化项目里使用 `plugin-upgrade-migrator` 迁移项目治理文件。

## 安装到 Claude Code

本地 checkout 先校验：

```bash
claude plugin validate .
```

开发时可以直接加载当前 checkout：

```bash
claude --plugin-dir .
```

分发时，用 `examples/claude-marketplace/.claude-plugin/marketplace.json` 创建 marketplace 仓库，然后用户添加 marketplace 并安装：

```text
/plugin marketplace add <your-marketplace-repo-or-path>
/plugin install codex-project-governor@project-governor-claude-marketplace
```

Claude 适配层提供：

- `/pg-init` 初始化治理文件。
- `/pg-route` 和 `/pg-context` 做任务路由与上下文检索。
- `/pg-quality` 做工程规范和就绪检查。
- `/pg-memory` 搜索治理记忆并记录 session learning。
- `/pg-upgrade`、`/pg-design`、`/pg-doctor` 处理升级、UI 门禁和诊断。

组件映射和维护规则见 `docs/compat/CLAUDE_CODE.md`。

## 安装到团队仓库

在目标仓库内执行：

```bash
mkdir -p plugins .agents/plugins
git clone https://github.com/yxhpy/codex-project-governor.git plugins/codex-project-governor
cp plugins/codex-project-governor/examples/repo-marketplace/marketplace.json .agents/plugins/marketplace.json
```

重启 Codex，打开 `/plugins`，选择仓库 marketplace，然后安装 **Project Governor**。

团队仓库 entry 也是 `source: local`。团队应通过 Git 或项目自己的 submodule/worktree 策略更新 `plugins/codex-project-governor`，然后重启 Codex，并用 `plugin-upgrade-migrator` 做项目治理迁移。

## 常用工作流

### 初始化空仓库

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

### 初始化已有仓库

```text
Use @project-governor init-existing-project.

Initialize this existing repository for strict iterative development.

Do not modify application code.
Infer conventions from the existing codebase.
Create governance files only.
```

也可以直接运行确定性初始化脚本：

```bash
python3 tools/init_project.py --mode existing --target /path/to/repo
```

### 把需求规划成一次迭代

```text
Use @project-governor iteration-planner.

Request:
<你的功能、修复或重构需求>

Treat this as an iteration, not a rewrite.
Find existing adjacent code and patterns first.
Create an ITERATION_PLAN.md.
Do not implement until the plan is complete.
```

### 用质量门加速开发

```text
Use @project-governor task-router.

Request:
<你的功能、修复或重构需求>

Choose the fastest safe workflow. Do not implement yet.
Return the route, lane, quality level, change budget, and required downstream skills.
```

推荐流水线：

- `task-router` 选择 route、lane、quality level 和 change budget。
- `route-guard` 验证 fast-lane 或 `micro_patch` 的实际 diff 是否越界。
- `subagent-activation` 为非平凡任务选择项目级 subagent 和模型策略。
- `context-pack-builder` 建上下文包。
- `pattern-reuse-engine` 固定必须复用的模式和禁止重复项。
- `test-first-synthesizer` 先规划行为、边界、错误、回归和集成/契约覆盖。
- `parallel-feature-builder` 先并行只读分析，再用一个有边界的实现者落地。
- `engineering-standards-governor` 检查文件规模、函数复杂度、mock 泄漏和测试断言质量。
- `quality-gate` 作为最终响应或 PR 前的硬检查。
- `repair-loop` 只在质量门失败时做有边界修复。
- `merge-readiness` 检查是否可以进入 PR 或 merge。

### 检查工程规范

```text
Use @project-governor engineering-standards-governor.

Check source size, function complexity, production mock leakage, test assertions, boundary-test planning, and reuse-first compliance before quality-gate completion.
```

确定性脚本：

```bash
python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project .
python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project . --diff-base main
```

### 使用 Harness v6.2.0

Harness v6.2.0 让 `task-router` 成为唯一 route 真源，并让运行时规划、docs manifest、章节级上下文索引、治理记忆搜索、session-learning ledger、会话状态、route guard、质量门、证据清单、DESIGN.md UI gate 和 merge-readiness 共用同一套契约。

```text
Use Project Governor Harness v6.2.0 to plan this change with DOCS_MANIFEST, section-level context retrieval, governed memory search, session state, evidence, route guard checks, and DESIGN.md UI gates when relevant.
```

核心验证命令：

```bash
python3 skills/context-indexer/scripts/build_context_index.py --project . --write
python3 skills/harness-doctor/scripts/doctor.py --project . --execution-readiness
python3 skills/evidence-manifest/scripts/write_evidence_manifest.py --project . --task-id demo --route standard_feature --validate
```

### 使用 GPT-5.5 自动编排

```text
Use @project-governor gpt55-auto-orchestrator.

Automatically choose the workflow, model plan, context budget, subagents, and quality gate for this request.
Read DOCS_MANIFEST, then query section-level context before reading large initialization docs.
```

初始化过的项目可以先生成或刷新紧凑上下文索引：

```bash
python3 skills/context-indexer/scripts/build_context_index.py --project . --write
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "dashboard widget"
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "为什么当时选择这个 checkout 流程" --memory-search --auto-build
```

`build_context_index.py --write` 会生成 `.project-governor/context/DOCS_MANIFEST.json`；`query_context_index.py` 会先返回 `recommended_sections`、`must_read_sections`、`progressive_read_plan` 和 `avoid_docs`，再把全文文件作为低置信度或章节不足时的后备。

记忆搜索模式只查受治理的项目资产，例如 `docs/memory/`、`docs/decisions/`、`tasks/`、发布记录和 `.project-governor/state/`，不默认扫描原始聊天记录。

### 记录 session learning

非平凡 session 开始时先查相关失败命令、重复错误和过期记忆；结束前如果出现命令失败、假设被纠正或发现记忆过期，应记录 session learning：

```bash
python3 skills/context-indexer/scripts/query_context_index.py --project . --request "<任务请求> command failures repeated mistakes stale memory" --memory-search --auto-build --format text
python3 skills/memory-compact/scripts/record_session_learning.py --project . --input /path/to/session-learning.json --apply
```

一次性失败命令进入 `.project-governor/state/COMMAND_LEARNINGS.json`；重复错误进入 `docs/memory/REPEATED_AGENT_MISTAKES.md`；失效或膨胀记忆进入 `.project-governor/state/MEMORY_HYGIENE.json`。这些文件会被 `--memory-search` 检索到，新 session 不需要用户再次提醒“记一下”。

### 升级前做版本研究

```text
Use @project-governor version-researcher.

Research candidate versions before upgrade-advisor is used.
Show skipped versions, evidence quality, relevant changes, migration risk, and user choices.
Do not modify manifests, lockfiles, application code, CI config, hooks, or rules.
```

### 升级前做升级建议

```text
Use @project-governor upgrade-advisor.

Request:
<你的功能、修复、迁移或维护目标>

Advisory only. Do not edit manifests or install packages.
Show which upgrades are relevant, risky, optional, deferred, or should be pinned.
```

### 升级已初始化的 Project Governor 项目

```text
Use @project-governor plugin-upgrade-migrator.

Show what is new, plan a safe migration, and do not overwrite my project customizations.
```

迁移器会读取 `CHANGELOG.md`、`releases/FEATURE_MATRIX.json`、`releases/MIGRATIONS.json` 和目标项目里的 `.project-governor/INSTALL_MANIFEST.json`。它只会自动应用安全的新增文件或未被用户修改的模板替换；用户改过的治理文件仍然进入手工审查或三方合并。

因为 `AGENTS.md` 承载强制项目行为，迁移器还会在最新插件模板和安装清单里的模板哈希不一致时暴露 `AGENTS.md` 模板漂移。未修改过的项目可以自动获得新规则，本地编辑过的 `AGENTS.md` 会保留为手工审查项。

### 检查项目卫生

v0.4.4 起，初始化默认使用 clean profile：只复制项目自己的治理文件，不把插件全局 `.codex/agents`、`.codex/prompts` 和 `.codex/config.toml` 写入目标项目。需要旧行为时显式使用 `--profile legacy-full`。

```bash
python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py --project /path/to/project --plugin-root /path/to/codex-project-governor
```

安全的生成型全局资产会被隔离到 `.project-governor/hygiene-quarantine/`，不会直接删除：

```bash
python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py --project /path/to/project --plugin-root /path/to/codex-project-governor --apply
```

### 干净重装或刷新治理项目

当需要重装用户级插件，或刷新已初始化项目的治理文件但不复制插件全局资产时，使用 `clean-reinstall-manager`。

安装或更新用户级插件 checkout 和本地 marketplace entry：

```bash
python3 tools/install_or_update_user_plugin.py --ref v6.2.0 --apply
```

生成用户级重装命令：

```bash
python3 skills/clean-reinstall-manager/scripts/generate_reinstall_instructions.py --ref v6.2.0
```

从项目外发现已治理仓库：

```bash
python3 skills/clean-reinstall-manager/scripts/discover_governed_projects.py --root "$HOME"
```

在已治理项目内生成安全刷新计划：

```bash
python3 skills/clean-reinstall-manager/scripts/refresh_project_governance.py --project . --plugin-root /path/to/codex-project-governor
```

### 治理 DESIGN.md 设计系统

当项目已经有 `DESIGN.md`，或准备把视觉身份、设计 token、UI 理由和实现约束沉淀成项目自己的 `DESIGN.md` 时，使用 `design-md-governor`。

```text
Use @project-governor design-md-governor.

Detect whether DESIGN.md exists.
Lint and summarize it if present.
Recommend an adoption plan if missing.
Do not create or overwrite DESIGN.md unless the user explicitly opts in.
```

无第三方依赖的备用脚本：

```bash
python3 skills/design-md-governor/scripts/lint_design_md.py DESIGN.md
python3 skills/design-md-governor/scripts/summarize_design_md.py DESIGN.md
python3 skills/design-md-governor/scripts/diff_design_md.py DESIGN.before.md DESIGN.md
```

### 用 DESIGN.md 约束 UI 编码

当任务涉及 React、Next.js、Tailwind、CSS、页面、组件、dashboard、landing page、响应式布局、视觉润色或 redesign 时，使用 `design-md-aesthetic-governor`。

```text
Use @project-governor design-md-aesthetic-governor.

Require Gemini/Stitch config from environment variables or project .env-design.
Read DESIGN.md before UI edits.
Run preflight to create .codex/design-md-governor/read-proof.json.
Use DESIGN.md tokens and rationale during implementation.
Verify drift after edits.
```

必需配置键：

```dotenv
GEMINI_BASE_URL=
GEMINI_API_KEY=
GEMINI_MODEL=
GEMINI_PROTOCOL=auto
STITCH_MCP_URL=https://stitch.googleapis.com/mcp
STITCH_MCP_API_KEY=
```

`.env-design` 是项目本地密钥配置，不得提交。环境变量优先于 `.env-design`。`GEMINI_PROTOCOL` 可以是 `auto`、`openai` 或 `gemini`；`gemini` 表示原生 Gemini `generateContent`，`openai` 表示 OpenAI-compatible 网关。通过第三方网关走原生 Gemini 时，`GEMINI_BASE_URL` 必须填该网关的 Gemini 协议根，例如提供 `/gemini/v1beta` 时填 `https://host/gemini`。`STITCH_MCP_URL` 默认是 `https://stitch.googleapis.com/mcp`。
如需不用 Gemini/Stitch、只用基础模式做前端，可以在 shell 环境变量或项目根 `.env-design` 中设置 `DESIGN_BASIC_MODE=1`；当 Codex hook 或 Windows 进程没有继承后来设置的 shell 变量时，`.env-design` 仍会被门禁直接读取。

完整模式的流程是：GPT/Codex 负责编排和代码实现，Stitch MCP 负责视觉原型探索，Gemini 负责按 `DESIGN.md` 做外部设计审查，最后 GPT/Codex 把通过的方向落到代码、测试和本地校验里。默认使用托管 Stitch MCP 端点，不需要本地安装 `stitch-mcp`、`npm` 或 `gcloud`；只有项目明确改成本地 MCP server 时才需要安装本地依赖。基础模式会跳过 Stitch 和 Gemini，但仍然要求读取 `DESIGN.md`、使用本地 lint、按 token 实现并做漂移检查。

真实服务冒烟测试：

```bash
python3 skills/design-md-aesthetic-governor/scripts/design_service_smoke.py --dry-run
python3 skills/design-md-aesthetic-governor/scripts/design_service_smoke.py --task "<service smoke task>"
python3 skills/design-md-aesthetic-governor/scripts/design_service_review.py --task "<ui task>"
```

### 实现新能力前做研究雷达

```text
Use @project-governor research-radar.

Research this candidate before implementation.
Show source quality, matched project needs, risk, maturity, recommendation, and user choices.
Do not modify application code, package manifests, lockfiles, hooks, rules, or plugin manifests.
```

### 压缩项目记忆

```text
Use @project-governor memory-compact.

Compact project memory from the last 7 days.
Read recent tasks, retros, execution logs, docs changes, PR feedback, and repeated mistakes.
Update only docs/memory/, docs/decisions/, and AGENTS.md when justified by evidence.
Do not modify application code.
```

## 确定性脚本

这些脚本只依赖 Python 标准库。

```bash
python3 tools/install_or_update_user_plugin.py --ref v6.2.0
python3 tools/init_project.py --mode existing --target /path/to/repo
python3 tools/init_project.py --mode existing --profile legacy-full --target /path/to/repo
python3 skills/project-hygiene-doctor/scripts/inspect_project_hygiene.py --project /path/to/project --plugin-root /path/to/codex-project-governor
python3 skills/convention-miner/scripts/detect_repo_conventions.py /path/to/repo
python3 skills/implementation-guard/scripts/check_iteration_compliance.py examples/guard-input.json
python3 skills/style-drift-check/scripts/check_style_drift.py examples/style-drift-input.json
python3 skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py examples/upgrade-candidates.json
python3 skills/plugin-upgrade-migrator/scripts/compare_features.py --current-version 0.4.1 --target-version 0.4.3 --feature-matrix releases/FEATURE_MATRIX.json
python3 skills/version-researcher/scripts/research_versions.py --manifest examples/version-research-manifest.json --request "Need better memory and subagent governance"
python3 skills/research-radar/scripts/score_research_candidates.py --manifest examples/research-candidates.json --need memory --need subagents --need research
python3 skills/task-router/scripts/classify_task.py examples/task-router-input.json
python3 skills/task-router/scripts/classify_task.py examples/task-router-micro-input.json
python3 skills/route-guard/scripts/check_route_guard.py examples/route-guard-micro-pass.json
python3 skills/subagent-activation/scripts/select_subagents.py examples/subagent-activation-standard-feature.json
python3 skills/context-pack-builder/scripts/build_context_pack.py . --request "dashboard widget"
python3 skills/pattern-reuse-engine/scripts/find_reuse_candidates.py . --request "dashboard widget"
python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project .
python3 skills/quality-gate/scripts/run_quality_gate.py examples/quality-gate-input.json
python3 skills/merge-readiness/scripts/check_merge_readiness.py examples/merge-readiness-input.json
python3 skills/coding-velocity-report/scripts/build_velocity_report.py examples/velocity-input.json
python3 skills/memory-compact/scripts/classify_memory_items.py examples/memory-candidates.json
python3 skills/memory-compact/scripts/record_session_learning.py --project . --input /path/to/session-learning.json
```

## 测试

```bash
python3 tests/selftest.py
```

也可以使用 Make 包装命令：

```bash
make test
```

测试覆盖：

- 插件 manifest 结构和版本。
- 用户级插件安装/更新脚本会规划本地 marketplace 更新，并保护有本地改动的 Git checkout。
- 每个 skill 的 `SKILL.md` 元数据。
- 必需模板文件。
- `.codex/rules/project.rules` 的合法决策值。
- 初始化脚本不会覆盖已有应用代码。
- implementation guard、style drift、engineering standards、upgrade advisor、version researcher、research radar、memory classifier 的核心输出。
- session learning 会把失败命令、重复错误和过期记忆候选写入可检索的记忆层。
- 中文文档入口和关键技能说明。

## 使用边界

- 这个仓库不是应用运行时，不提供 Web UI、后端服务或 HTTP API。
- 默认不新增依赖；确定性脚本应保持标准库实现。
- 默认初始化保持 clean profile；旧式复制 `.codex` agents/prompts/config 资产需要显式使用 `--profile legacy-full`。
- 初始化已有仓库时不修改应用代码。
- 升级、版本变更、hook/rule 行为变化必须先经过 advisory 流程。
- durable memory 只能写入有证据的事实；不确定内容应进入 open questions。

## 更多中文说明

- [中文使用指南](docs/zh-CN/USAGE.md)
- [v0.3 Research Brief](docs/research/V0.3_RESEARCH_BRIEF.md)
