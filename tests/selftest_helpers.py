#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
TIMEOUT = 10

REQUIRED_SKILLS = {
    "version-researcher",
    "plugin-upgrade-migrator",
    "project-hygiene-doctor",
    "clean-reinstall-manager",
    "design-md-governor",
    "design-md-aesthetic-governor",
    "gpt55-auto-orchestrator",
    "context-indexer",
    "research-radar",
    "task-router",
    "route-guard",
    "subagent-activation",
    "context-pack-builder",
    "pattern-reuse-engine",
    "parallel-feature-builder",
    "test-first-synthesizer",
    "engineering-standards-governor",
    "quality-gate",
    "repair-loop",
    "merge-readiness",
    "coding-velocity-report",
    "session-lifecycle",
    "evidence-manifest",
    "harness-doctor",
}
ALLOWED_VISIBILITY = {"primary", "workflow", "internal", "advanced", "deprecated"}
ALLOWED_CATEGORIES = {
    "context",
    "design",
    "implementation",
    "initialization",
    "maintenance",
    "memory",
    "metrics",
    "orchestration",
    "quality",
    "research",
    "review",
    "state",
    "upgrade",
}
MANAGED_ASSET_PATHS = [
    "design-md/DESIGN.md.template",
    "design-md/DESIGN_MD_POLICY.md",
    "runtime/GPT55_AUTO_ORCHESTRATION_POLICY.md",
    "runtime/HARNESS_V6_POLICY.md",
]
REQUIRED_TEMPLATE_PATHS = [
    "AGENTS.md",
    "CLAUDE.md",
    "docs/project/CHARTER.md",
    "docs/conventions/ITERATION_CONTRACT.md",
    "docs/conventions/CONVENTION_MANIFEST.md",
    "docs/architecture/ARCHITECTURE.md",
    "docs/memory/PROJECT_MEMORY.md",
    "docs/memory/OPEN_QUESTIONS.md",
    "docs/decisions/ADR-0000-template.md",
    "tasks/_template/ITERATION_PLAN.md",
    ".codex/prompts/memory-compact.md",
    ".codex/prompts/upgrade-advisor.md",
    ".codex/prompts/plugin-upgrade-migrator.md",
    ".codex/prompts/project-hygiene-doctor.md",
    ".codex/prompts/clean-reinstall-manager.md",
    ".codex/prompts/design-md-governor.md",
    ".codex/prompts/design-md-aesthetic-governor.md",
    ".codex/prompts/gpt55-auto-orchestrator.md",
    ".codex/prompts/context-indexer.md",
    ".codex/prompts/session-lifecycle.md",
    ".codex/prompts/evidence-manifest.md",
    ".codex/prompts/harness-doctor.md",
    ".codex/hooks/check_iteration_compliance.py",
    ".codex/hooks/design_md_codex_hook.py",
    ".codex/hooks.json",
    ".project-governor/INSTALL_MANIFEST.json",
    ".project-governor/runtime/GPT55_RUNTIME_MODE.json",
    ".project-governor/evidence/_template/EVIDENCE.json",
    ".project-governor/evidence/_template/ACCEPTANCE_MAP.md",
    ".project-governor/state/FEATURES.json",
    ".project-governor/state/AGENTS.json",
    ".project-governor/state/ISSUES.json",
    ".project-governor/state/COMMAND_LEARNINGS.json",
    ".project-governor/state/MEMORY_HYGIENE.json",
    ".project-governor/state/PROGRESS.md",
    ".project-governor/state/SESSION.json",
    ".project-governor/state/QUALITY_SCORE.json",
    "docs/upgrades/UPGRADE_POLICY.md",
    "docs/upgrades/UPGRADE_REGISTER.md",
    "docs/upgrades/PLUGIN_UPGRADE_POLICY.md",
    "docs/upgrades/CLEAN_REINSTALL_POLICY.md",
    "docs/research/RESEARCH_POLICY.md",
    "docs/research/RESEARCH_REGISTER.md",
    "docs/upgrades/RELEASE_RESEARCH_POLICY.md",
    "docs/upgrades/RELEASE_RESEARCH_REPORT.md",
    "docs/quality/QUALITY_GATE_POLICY.md",
    "docs/quality/ENGINEERING_STANDARDS_POLICY.md",
    "docs/quality/CHANGE_BUDGET_POLICY.md",
    "docs/quality/TESTING_ACCELERATION_POLICY.md",
    "docs/quality/ACCELERATION_POLICY.md",
    "docs/quality/ROUTE_GUARD_POLICY.md",
    "docs/quality/SUBAGENT_ACTIVATION_POLICY.md",
    "docs/quality/DESIGN_MD_AESTHETIC_GATE_POLICY.md",
    "docs/quality/PROJECT_HYGIENE_POLICY.md",
    "tasks/_template/TASK_ROUTE.md",
    "tasks/_template/CONTEXT_PACK.md",
    "tasks/_template/PATTERN_REUSE_PLAN.md",
    "tasks/_template/TEST_PLAN.md",
    "tasks/_template/ENGINEERING_STANDARDS_REPORT.md",
    "tasks/_template/CHANGE_BUDGET.md",
    "tasks/_template/QUALITY_REPORT.md",
    "tasks/_template/REPAIR_LOG.md",
    "tasks/_template/MERGE_READINESS.md",
    "tasks/_template/VELOCITY_REPORT.md",
    "tasks/_template/ROUTE_GUARD_REPORT.md",
    "artifacts/ARTIFACT_TEMPLATES.json",
    "artifacts/schemas/iteration_plan_v1.schema.json",
    ".codex/prompts/research-radar.md",
    ".codex/prompts/version-researcher.md",
    ".codex/prompts/task-router.md",
    ".codex/prompts/route-guard.md",
    ".codex/prompts/subagent-activation.md",
    ".codex/prompts/context-pack-builder.md",
    ".codex/prompts/pattern-reuse-engine.md",
    ".codex/prompts/parallel-feature-builder.md",
    ".codex/prompts/test-first-synthesizer.md",
    ".codex/prompts/engineering-standards-governor.md",
    ".codex/prompts/quality-gate.md",
    ".codex/prompts/repair-loop.md",
    ".codex/prompts/merge-readiness.md",
    ".codex/prompts/coding-velocity-report.md",
    ".codex/config.toml",
    ".codex/agents/context-scout.toml",
    ".codex/agents/pattern-reuse-scout.toml",
    ".codex/agents/risk-scout.toml",
    ".codex/agents/quality-reviewer.toml",
    ".codex/agents/implementation-writer.toml",
]


def run_json(command: list[str], check: bool = True) -> tuple[int, dict[str, Any]]:
    proc = subprocess.run(command, text=True, capture_output=True, check=check, timeout=TIMEOUT)
    return proc.returncode, json.loads(proc.stdout)


def assert_task_router_acceleration(case: Any) -> None:
    _, route = run_json([PY, str(ROOT / "skills" / "task-router" / "scripts" / "classify_task.py"), str(ROOT / "examples" / "task-router-input.json")])
    case.assertIn(route["route"], {"ui_change", "standard_feature"})
    case.assertEqual(route["quality_level"], "standard")
    case.assertIn("quality-gate", route["required_skills"])
    case.assertIn("engineering-standards-governor", route["required_skills"])

    _, risk = run_json([PY, str(ROOT / "skills" / "task-router" / "scripts" / "classify_task.py"), str(ROOT / "examples" / "task-router-risk-input.json")])
    case.assertEqual(risk["route"], "risky_feature")
    case.assertEqual(risk["quality_level"], "strict")
    case.assertIn("risk_domain", risk["risk_signals"])


def write_context_pack_fixture(repo: Path) -> None:
    (repo / "src" / "components").mkdir(parents=True)
    (repo / "src" / "services").mkdir(parents=True)
    (repo / "docs").mkdir()
    (repo / "src" / "components" / "DashboardChart.tsx").write_text("export function DashboardChart() { return null }\n", encoding="utf-8")
    (repo / "src" / "services" / "dashboardService.ts").write_text("export const dashboardService = { load() { return [] } }\n", encoding="utf-8")
    (repo / "src" / "DashboardChart.test.tsx").write_text("test('dashboard chart', () => {})\n", encoding="utf-8")
    (repo / "docs" / "dashboard.md").write_text("Dashboard widget behavior.\n", encoding="utf-8")


def assert_context_pack_result(case: Any, context: dict[str, Any]) -> None:
    case.assertIn("src/components/DashboardChart.tsx", {item["path"] for item in context["must_read"]})
    case.assertTrue(context["related_tests"])
    case.assertIn("token_budget", context)
    case.assertTrue(context["token_budget"]["full_doc_requires_reason"])
    case.assertIn("compression_policy", context)


def assert_reuse_result(case: Any, reuse: dict[str, Any]) -> None:
    case.assertIn("DashboardChart", {item["name"] for item in reuse["reuse_candidates"]})
    case.assertTrue(reuse["forbidden_duplicates"])


def assert_context_pack_and_reuse(case: Any) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        write_context_pack_fixture(repo)
        _, context = run_json([PY, str(ROOT / "skills" / "context-pack-builder" / "scripts" / "build_context_pack.py"), str(repo), "--request", "dashboard chart widget"])
        _, reuse = run_json([PY, str(ROOT / "skills" / "pattern-reuse-engine" / "scripts" / "find_reuse_candidates.py"), str(repo), "--request", "dashboard chart widget"])
        assert_context_pack_result(case, context)
        assert_reuse_result(case, reuse)


def assert_quality_gate_example_fails(case: Any) -> None:
    returncode, gate = run_json([PY, str(ROOT / "skills" / "quality-gate" / "scripts" / "run_quality_gate.py"), str(ROOT / "examples" / "quality-gate-input.json")], check=False)
    case.assertNotEqual(returncode, 0)
    case.assertEqual(gate["status"], "fail")
    gate_types = {item["type"] for item in gate["findings"]}
    case.assertIn("change_budget_exceeded", gate_types)
    case.assertIn("new_file_budget_exceeded", gate_types)


def assert_merge_readiness_example(case: Any) -> None:
    _, ready = run_json([PY, str(ROOT / "skills" / "merge-readiness" / "scripts" / "check_merge_readiness.py"), str(ROOT / "examples" / "merge-readiness-input.json")])
    case.assertEqual(ready["status"], "ready")


def assert_velocity_example(case: Any) -> None:
    _, velocity = run_json([PY, str(ROOT / "skills" / "coding-velocity-report" / "scripts" / "build_velocity_report.py"), str(ROOT / "examples" / "velocity-input.json")])
    case.assertGreaterEqual(velocity["quality_score"], 70)
    case.assertGreaterEqual(velocity["velocity_score"], 70)


def assert_acceleration_tools(case: Any) -> None:
    assert_task_router_acceleration(case)
    assert_context_pack_and_reuse(case)
    assert_quality_gate_example_fails(case)
    assert_merge_readiness_example(case)
    assert_velocity_example(case)
