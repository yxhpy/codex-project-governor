# Convention Manifest

## Source of truth

- Product identity: `docs/project/CHARTER.md`
- Architecture: `docs/architecture/ARCHITECTURE.md`
- API contracts: `docs/architecture/API_CONTRACTS.md`
- Claude Code compatibility: `docs/compat/CLAUDE_CODE.md`
- Skill audience catalog: `skills/CATALOG.json`
- Code style: `docs/conventions/CODE_STYLE.md`
- UI style: `docs/conventions/UI_STYLE.md`
- Component registry: `docs/conventions/COMPONENT_REGISTRY.md`
- Pattern registry: `docs/conventions/PATTERN_REGISTRY.md`
- DESIGN.md policy: `managed-assets/design-md/DESIGN_MD_POLICY.md`
- DESIGN.md aesthetic gate policy: `docs/quality/DESIGN_MD_AESTHETIC_GATE_POLICY.md`
- GPT-5.5 runtime policy: `managed-assets/runtime/GPT55_AUTO_ORCHESTRATION_POLICY.md`
- Harness v6 runtime policy: `managed-assets/runtime/HARNESS_V6_POLICY.md`
- Harness v6 contract: `docs/harness/HARNESS_V6.md`
- GPT-5.5 runtime mode template: `templates/.project-governor/runtime/GPT55_RUNTIME_MODE.json`
- Execution policy template: `templates/.project-governor/runtime/EXECUTION_POLICY.json`
- Harness v6 state templates: `templates/.project-governor/state/`
- Harness v6 evidence templates: `templates/.project-governor/evidence/_template/`
- Generated docs manifest: `.project-governor/context/DOCS_MANIFEST.json`
- Iteration contract: `docs/conventions/ITERATION_CONTRACT.md`
- Upgrade policy: `docs/upgrades/UPGRADE_POLICY.md`
- Upgrade register: `docs/upgrades/UPGRADE_REGISTER.md`
- Plugin upgrade policy: `templates/docs/upgrades/PLUGIN_UPGRADE_POLICY.md`
- Clean reinstall policy: `templates/docs/upgrades/CLEAN_REINSTALL_POLICY.md`
- Release feature matrix: `releases/FEATURE_MATRIX.json`
- Release migrations: `releases/MIGRATIONS.json`
- Current versioned release notes: `releases/6.2.4.md`
- Harness v6 release notes: `releases/6.0.0.md`
- Harness v6 release notes: `releases/HARNESS_V6_RELEASE_NOTES.md`
- Generated artifact helpers: `tools/new_governance_artifact.py`, `tools/render_governance_artifact.py`, `tools/update_governance_artifact.py`
- User plugin install/update helper: `tools/install_or_update_user_plugin.py`
- Skill catalog analyzer: `tools/analyze_skill_catalog.py`
- Session learning recorder: `skills/memory-compact/scripts/record_session_learning.py`
- Research brief: `docs/research/V0.3_RESEARCH_BRIEF.md`
- Acceleration policy: `docs/quality/ACCELERATION_POLICY.md`
- Testing acceleration policy: `docs/quality/TESTING_ACCELERATION_POLICY.md`
- Engineering standards policy: `docs/quality/ENGINEERING_STANDARDS_POLICY.md`
- Change budget policy: `docs/quality/CHANGE_BUDGET_POLICY.md`
- Quality gate policy: `docs/quality/QUALITY_GATE_POLICY.md`
- Project hygiene policy template: `templates/docs/quality/PROJECT_HYGIENE_POLICY.md`
- Route guard policy: `docs/quality/ROUTE_GUARD_POLICY.md`
- Subagent activation policy: `docs/quality/SUBAGENT_ACTIVATION_POLICY.md`
- Smart routing guard brief: `docs/research/V0.4.1_SMART_ROUTING_GUARD.md`
- Explicit subagent activation brief: `docs/research/V0.4.2_EXPLICIT_SUBAGENT_ACTIVATION.md`

If implementation conflicts with these files, create or update a decision record first.

## Confirmed Repository Conventions

- This is a plugin/template repository, not an application repository.
- Public plugin metadata starts in `.codex-plugin/plugin.json`.
- Claude Code plugin metadata starts in `.claude-plugin/plugin.json`; Claude-specific commands, agents, skills, and hooks live under `claude/`.
- Skill workflows are documented in `skills/<skill>/SKILL.md`.
- Skill audience and documentation grouping metadata is documented in `skills/CATALOG.json`.
- README skill grouping must follow `skills/CATALOG.json` visibility and is validated by `tools/analyze_skill_catalog.py`.
- Skill catalog health, resolved consolidation groups, and remaining consolidation candidates are inspected by `tools/analyze_skill_catalog.py`.
- Deterministic script helpers are CLI modules under `tools/` and `skills/*/scripts/`.
- Governance files copied into downstream repositories come from `templates/`.
- Optional plugin-owned design-system support files live under `managed-assets/` and are not copied into downstream repositories by default.
- Optional plugin-owned runtime policy files live under `managed-assets/runtime/`; project runtime state belongs under `.project-governor/runtime/`.
- Harness v6 project state and evidence templates live under `templates/.project-governor/state/` and `templates/.project-governor/evidence/`.
- Example JSON inputs are stored under `examples/`.
- Tests use Python standard-library `unittest` in `tests/selftest.py`.
- Engineering standards checks are dependency-free Python scripts and should remain conservative, additive, and documented in API contracts.
- Execution policy checks are dependency-free Python scripts and should convert user-selected command tools/transports into quality-gate findings before release, deploy, or publish completion.

## Evidence

- `README.md`
- `.codex-plugin/plugin.json`
- `.claude-plugin/plugin.json`
- `tests/selftest.py`
- `tools/init_project.py`
- `skills/*/SKILL.md`
