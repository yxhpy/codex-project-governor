# codex-project-governor

中文 | [English](README.md)

`codex-project-governor` 是一个 Codex 插件，用来把仓库变成可自我治理的 Codex 项目。它会把项目规则、约定、决策、风险、记忆、迭代计划和检查入口放进版本控制，让后续 Codex 会话能按同一套规则继续工作，而不是每次重新摸索。

当前版本：`0.4.3`

## 它解决什么问题

普通仓库在长期使用 Codex 时容易出现这些问题：

- 新会话忘记项目规则和历史决策。
- 小改动被做成重写。
- 风格、架构、组件和 API 契约逐渐漂移。
- 升级依赖、工具或 SDK 前缺少证据和风险分级。
- 有用经验只留在聊天记录里，没有进入仓库。

Project Governor 的做法是把治理资产放在仓库内：

- `AGENTS.md`：项目级行为规则。
- `docs/conventions/`：代码、架构、UI、组件、迭代约定。
- `docs/memory/`：可追溯的项目记忆、风险和常见错误。
- `docs/decisions/`：ADR/PDR 决策记录。
- `docs/upgrades/`：升级策略、升级登记和发布研究。
- `docs/research/`：候选能力研究、证据质量和采纳建议。
- `tasks/`：每次迭代的计划、日志和复盘。
- `skills/`：可复用的 Codex 工作流。
- `templates/`：初始化目标仓库时复制的治理模板。

## 核心能力

- 初始化空仓库或已有仓库，只写治理文件，不改应用代码。
- 挖掘已有仓库的技术栈、目录结构、测试、样式和约定。
- 强制非平凡改动先做迭代计划，避免重写式开发。
- 检查实现风险、样式漂移、架构漂移和 PR 治理问题。
- 在升级前进行版本距离、跳过版本、风险和需求相关性分析。
- 在实现新能力前做研究雷达，判断 `adopt_now`、`spike`、`watch` 或 `reject`。
- 用任务路由、微补丁路由、route guard、自动 subagent 激活、插件升级迁移器、上下文包、模式复用、并行实现、质量门、修复循环和合并就绪检查，把提速约束在质量边界内。
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
| `version-researcher` | 在 upgrade-advisor 前研究候选版本、跳过版本、证据质量和迁移风险。 |
| `research-radar` | 在实现新能力前研究候选方案、证据质量、项目匹配度和风险。 |
| `task-router` | 把需求分流到最快且安全的 Project Governor 工作流、通道、质量等级和变更预算。 |
| `route-guard` | 验证实际 diff 是否仍符合 task-router 选定的路由，尤其是 `micro_patch` 和 fast-lane 改动。 |
| `subagent-activation` | 按 route、workflow、风险、质量等级和置信度选择项目级 subagent 与模型策略，避免用户手动列 subagent。 |
| `context-pack-builder` | 构建最小任务上下文包，减少 Codex 和子代理重复探索仓库。 |
| `pattern-reuse-engine` | 找出现有组件、服务、hook、schema、测试和样式模式，避免重复造新模式。 |
| `parallel-feature-builder` | 用质量门约束的子代理流水线实现功能：先只读分析，再单一实现者，再测试、审查和修复。 |
| `test-first-synthesizer` | 按现有测试风格先产出目标测试计划或测试骨架。 |
| `quality-gate` | 运行分层质量检查，覆盖迭代合规、漂移、变更预算、测试、文档和记忆更新。 |
| `repair-loop` | 在质量门失败时执行有边界的修复循环，不删除测试、不削弱断言、不扩大范围。 |
| `merge-readiness` | 检查任务或分支是否 PR-ready，覆盖 blocker、质量门、文档、记忆、测试、预算和审批。 |
| `coding-velocity-report` | 记录上下文时间、首次补丁时间、修复轮次、质量门通过率、补丁规模和复用比例。 |

## 安装到个人 Codex

把插件克隆到个人插件目录：

```bash
mkdir -p ~/.codex/plugins
git clone https://github.com/yxhpy/codex-project-governor.git ~/.codex/plugins/codex-project-governor
```

创建或更新 `~/.agents/plugins/marketplace.json`：

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

## 安装到团队仓库

在目标仓库内执行：

```bash
mkdir -p plugins .agents/plugins
git clone https://github.com/yxhpy/codex-project-governor.git plugins/codex-project-governor
cp plugins/codex-project-governor/examples/repo-marketplace/marketplace.json .agents/plugins/marketplace.json
```

重启 Codex，打开 `/plugins`，选择仓库 marketplace，然后安装 **Project Governor**。

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
- `test-first-synthesizer` 先规划行为和回归覆盖。
- `parallel-feature-builder` 先并行只读分析，再用一个有边界的实现者落地。
- `quality-gate` 作为最终响应或 PR 前的硬检查。
- `repair-loop` 只在质量门失败时做有边界修复。
- `merge-readiness` 检查是否可以进入 PR 或 merge。

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
python3 tools/init_project.py --mode existing --target /path/to/repo
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
python3 skills/quality-gate/scripts/run_quality_gate.py examples/quality-gate-input.json
python3 skills/merge-readiness/scripts/check_merge_readiness.py examples/merge-readiness-input.json
python3 skills/coding-velocity-report/scripts/build_velocity_report.py examples/velocity-input.json
python3 skills/memory-compact/scripts/classify_memory_items.py examples/memory-candidates.json
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
- 每个 skill 的 `SKILL.md` 元数据。
- 必需模板文件。
- `.codex/rules/project.rules` 的合法决策值。
- 初始化脚本不会覆盖已有应用代码。
- implementation guard、style drift、upgrade advisor、version researcher、research radar、memory classifier 的核心输出。
- 中文文档入口和关键技能说明。

## 使用边界

- 这个仓库不是应用运行时，不提供 Web UI、后端服务或 HTTP API。
- 默认不新增依赖；确定性脚本应保持标准库实现。
- 初始化已有仓库时不修改应用代码。
- 升级、版本变更、hook/rule 行为变化必须先经过 advisory 流程。
- durable memory 只能写入有证据的事实；不确定内容应进入 open questions。

## 更多中文说明

- [中文使用指南](docs/zh-CN/USAGE.md)
- [v0.3 Research Brief](docs/research/V0.3_RESEARCH_BRIEF.md)
