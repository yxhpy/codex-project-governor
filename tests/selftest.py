#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
TIMEOUT = 10


class ProjectGovernorSelfTest(unittest.TestCase):
    def test_plugin_manifest(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "codex-project-governor")
        self.assertEqual(manifest["version"], "6.2.0")
        self.assertIn("Harness v6.2.0", manifest["description"])
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertIn("interface", manifest)
        self.assertIn("defaultPrompt", manifest["interface"])
        feature_matrix = json.loads((ROOT / "releases" / "FEATURE_MATRIX.json").read_text(encoding="utf-8"))
        self.assertEqual(feature_matrix["current_latest"], "6.2.0")
        versions = {item["version"] for item in feature_matrix["versions"]}
        self.assertIn("6.2.0", versions)
        self.assertTrue((ROOT / "releases" / "6.2.0.md").exists())

    def test_skills_have_metadata(self) -> None:
        skill_dirs = [p for p in (ROOT / "skills").iterdir() if p.is_dir()]
        self.assertGreaterEqual(len(skill_dirs), 35)
        names = {p.name for p in skill_dirs}
        for required in {
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
        }:
            self.assertIn(required, names)
        for skill_dir in skill_dirs:
            skill_md = skill_dir / "SKILL.md"
            self.assertTrue(skill_md.exists(), skill_dir)
            text = skill_md.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), skill_md)
            self.assertIn("name:", text)
            self.assertIn("description:", text)

    def test_required_templates_exist(self) -> None:
        required = [
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
        for rel in required:
            self.assertTrue((ROOT / "templates" / rel).exists(), rel)

    def test_managed_assets_exist(self) -> None:
        required = [
            "design-md/DESIGN.md.template",
            "design-md/DESIGN_MD_POLICY.md",
            "runtime/GPT55_AUTO_ORCHESTRATION_POLICY.md",
            "runtime/HARNESS_V6_POLICY.md",
        ]
        for rel in required:
            self.assertTrue((ROOT / "managed-assets" / rel).exists(), rel)

    def test_chinese_docs_exist(self) -> None:
        readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        usage = (ROOT / "docs" / "zh-CN" / "USAGE.md").read_text(encoding="utf-8")
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("README.zh-CN.md", english)
        self.assertIn("Project Governor", readme)
        self.assertIn("research-radar", readme)
        self.assertIn("version-researcher", readme)
        self.assertIn("6.2.0", readme)
        self.assertIn("Claude Code", readme)
        self.assertIn("task-router", readme)
        self.assertIn("route-guard", readme)
        self.assertIn("subagent-activation", readme)
        self.assertIn("plugin-upgrade-migrator", readme)
        self.assertIn("project-hygiene-doctor", readme)
        self.assertIn("clean-reinstall-manager", readme)
        self.assertIn("design-md-governor", readme)
        self.assertIn("design-md-aesthetic-governor", readme)
        self.assertIn("gpt55-auto-orchestrator", readme)
        self.assertIn("context-indexer", readme)
        self.assertIn("session-lifecycle", readme)
        self.assertIn("evidence-manifest", readme)
        self.assertIn("harness-doctor", readme)
        self.assertIn("engineering-standards-governor", readme)
        self.assertIn("init-existing-project", usage)
        self.assertIn("quality-gate", usage)
        self.assertIn("design-md-governor", usage)
        self.assertIn("design-md-aesthetic-governor", usage)
        self.assertIn("gpt55-auto-orchestrator", usage)
        self.assertIn("context-indexer", usage)
        self.assertIn("memory-compact", usage)
        self.assertIn("record_session_learning", usage)
        self.assertIn("engineering-standards-governor", usage)

    def test_project_rules_use_valid_decisions(self) -> None:
        rules = (ROOT / "templates" / ".codex" / "rules" / "project.rules").read_text(encoding="utf-8")
        decisions = re.findall(r'decision="([^"]+)"', rules)
        self.assertGreater(len(decisions), 0)
        self.assertEqual(set(decisions) - {"allow", "prompt"}, set())
        self.assertNotIn("deny", decisions)

    def test_init_project_preserves_application_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            source = repo / "src" / "main.ts"
            package_json = repo / "package.json"
            source.write_text("export const x = 1;\n", encoding="utf-8")
            package_json.write_text('{"name":"fixture"}\n', encoding="utf-8")
            process = subprocess.run(
                [PY, str(ROOT / "tools" / "init_project.py"), "--mode", "existing", "--target", str(repo), "--json"],
                text=True,
                capture_output=True,
                check=True,
            )
            result = json.loads(process.stdout)
            self.assertEqual(source.read_text(encoding="utf-8"), "export const x = 1;\n")
            self.assertEqual(package_json.read_text(encoding="utf-8"), '{"name":"fixture"}\n')
            self.assertEqual(result["profile"], "clean")
            self.assertIn("skipped", result)
            self.assertIn("skipped_application", result)
            self.assertIn("skipped_global", result)
            self.assertTrue((repo / "AGENTS.md").exists())
            self.assertTrue((repo / "CLAUDE.md").exists())
            self.assertTrue((repo / "docs" / "conventions" / "ITERATION_CONTRACT.md").exists())
            self.assertTrue((repo / ".codex" / "rules" / "project.rules").exists())
            self.assertTrue((repo / ".codex" / "hooks" / "check_iteration_compliance.py").exists())
            self.assertTrue((repo / ".codex" / "hooks.json").exists())
            self.assertTrue((repo / ".project-governor" / "runtime" / "GPT55_RUNTIME_MODE.json").exists())
            self.assertFalse((repo / ".codex" / "agents").exists())

    def test_iteration_guard_detects_blockers(self) -> None:
        proc = subprocess.run(
            [PY, str(ROOT / "skills" / "implementation-guard" / "scripts" / "check_iteration_compliance.py"), str(ROOT / "examples" / "guard-input.json")],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        types = {item["type"] for item in data["findings"]}
        self.assertIn("rewrite_risk", types)
        self.assertIn("dependency_change_requires_decision", types)
        self.assertIn("new_files_without_justification", types)
        self.assertIn("public_contract_change_requires_decision", types)

    def test_style_drift_detects_blockers(self) -> None:
        proc = subprocess.run(
            [PY, str(ROOT / "skills" / "style-drift-check" / "scripts" / "check_style_drift.py"), str(ROOT / "examples" / "style-drift-input.json")],
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        types = {item["type"] for item in data["findings"]}
        self.assertIn("unregistered_components", types)
        self.assertIn("raw_color_literals", types)
        self.assertIn("unapproved_style_systems", types)

    def test_upgrade_advisor(self) -> None:
        proc = subprocess.run(
            [PY, str(ROOT / "skills" / "upgrade-advisor" / "scripts" / "analyze_upgrade_candidates.py"), str(ROOT / "examples" / "upgrade-candidates.json")],
            text=True,
            capture_output=True,
            check=True,
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["status"], "review_required")
        recommendations = {item["name"]: item["recommendation"] for item in data["candidates"]}
        self.assertEqual(recommendations["lodash"], "upgrade_required")
        self.assertIn(recommendations["react"], {"recommend_upgrade", "consider_upgrade"})
        self.assertEqual(recommendations["eslint"], "defer")
        react = next(item for item in data["candidates"] if item["name"] == "react")
        self.assertEqual(react["version_distance"]["major"], 1)
        self.assertEqual(react["skipped_versions"], 3)
        self.assertIn("plan_upgrade_iteration", react["choices"])

    def test_memory_classifier(self) -> None:
        proc = subprocess.run(
            [PY, str(ROOT / "skills" / "memory-compact" / "scripts" / "classify_memory_items.py"), str(ROOT / "examples" / "memory-candidates.json")],
            text=True,
            capture_output=True,
            check=True,
        )
        classes = {item["classification"] for item in json.loads(proc.stdout)}
        self.assertIn("durable_fact", classes)
        self.assertIn("decision", classes)
        self.assertIn("open_question", classes)
        self.assertIn("repeated_mistake", classes)
        self.assertIn("secret_or_sensitive", classes)

    def test_convention_miner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src" / "App.tsx").write_text("export function App() { return null }\n", encoding="utf-8")
            (repo / "package.json").write_text(json.dumps({"dependencies": {"react": "latest"}, "devDependencies": {"vitest": "latest"}}), encoding="utf-8")
            (repo / "pnpm-lock.yaml").write_text("lockfileVersion: '9'\n", encoding="utf-8")
            proc = subprocess.run(
                [PY, str(ROOT / "skills" / "convention-miner" / "scripts" / "detect_repo_conventions.py"), str(repo)],
                text=True,
                capture_output=True,
                check=True,
            )
            data = json.loads(proc.stdout)
            self.assertIn("TypeScript", data["languages"])
            self.assertIn("src", data["source_roots"])
            self.assertIn({"name": "pnpm", "evidence": "pnpm-lock.yaml"}, data["package_manager"])

    def test_version_researcher(self) -> None:
        proc = subprocess.run(
            [
                PY,
                str(ROOT / "skills" / "version-researcher" / "scripts" / "research_versions.py"),
                "--manifest",
                str(ROOT / "examples" / "version-research-manifest.json"),
                "--request",
                "研究下个版本是否值得升级，尤其要支持版本研究和升级建议",
            ],
            text=True,
            capture_output=True,
            check=True,
            timeout=TIMEOUT,
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["current_version"], "0.2.0")
        self.assertEqual(data["versions_behind"], 2)
        self.assertEqual(data["overall_recommendation"]["action"], "recommend_upgrade")
        self.assertEqual(data["overall_recommendation"]["target_version"], "0.3.0")
        candidates = {item["version"]: item for item in data["candidate_versions"]}
        self.assertEqual(candidates["0.3.0"]["evidence_quality"]["label"], "primary")
        self.assertIn("version_research", candidates["0.3.0"]["matched_needs"])
        self.assertEqual(candidates["1.0.0"]["recommendation"], "preview_in_isolation")
        choices = {choice["id"] for choice in data["user_choices"]}
        self.assertIn("preview", choices)
        self.assertIn("plan", choices)

    def test_research_radar(self) -> None:
        proc = subprocess.run(
            [
                PY,
                str(ROOT / "skills" / "research-radar" / "scripts" / "score_research_candidates.py"),
                "--manifest",
                str(ROOT / "examples" / "research-candidates.json"),
                "--need",
                "memory",
                "--need",
                "subagents",
                "--need",
                "research",
            ],
            text=True,
            capture_output=True,
            check=True,
            timeout=TIMEOUT,
        )
        data = json.loads(proc.stdout)
        recommendations = {item["id"]: item["recommendation"] for item in data["candidates"]}
        self.assertEqual(recommendations["research-radar-skill"], "adopt_now")
        self.assertIn(recommendations["codex-subagent-audit-profiles"], {"adopt_now", "spike"})
        self.assertIn(recommendations["strict-hooks-mode"], {"spike", "watch"})
        self.assertIn("research-radar-skill", data["summary"]["adopt_now"])
        labels = {choice["id"] for choice in data["user_choices"]}
        self.assertIn("1", labels)
        self.assertIn("4", labels)

    def test_acceleration_tools(self) -> None:
        route_proc = subprocess.run(
            [PY, str(ROOT / "skills" / "task-router" / "scripts" / "classify_task.py"), str(ROOT / "examples" / "task-router-input.json")],
            text=True,
            capture_output=True,
            check=True,
            timeout=TIMEOUT,
        )
        route = json.loads(route_proc.stdout)
        self.assertIn(route["route"], {"ui_change", "standard_feature"})
        self.assertEqual(route["quality_level"], "standard")
        self.assertIn("quality-gate", route["required_skills"])
        self.assertIn("engineering-standards-governor", route["required_skills"])

        risk_proc = subprocess.run(
            [PY, str(ROOT / "skills" / "task-router" / "scripts" / "classify_task.py"), str(ROOT / "examples" / "task-router-risk-input.json")],
            text=True,
            capture_output=True,
            check=True,
            timeout=TIMEOUT,
        )
        risk = json.loads(risk_proc.stdout)
        self.assertEqual(risk["route"], "risky_feature")
        self.assertEqual(risk["quality_level"], "strict")
        self.assertIn("risk_domain", risk["risk_signals"])

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src" / "components").mkdir(parents=True)
            (repo / "src" / "services").mkdir(parents=True)
            (repo / "docs").mkdir()
            (repo / "src" / "components" / "DashboardChart.tsx").write_text(
                "export function DashboardChart() { return null }\n", encoding="utf-8"
            )
            (repo / "src" / "services" / "dashboardService.ts").write_text(
                "export const dashboardService = { load() { return [] } }\n", encoding="utf-8"
            )
            (repo / "src" / "DashboardChart.test.tsx").write_text("test('dashboard chart', () => {})\n", encoding="utf-8")
            (repo / "docs" / "dashboard.md").write_text("Dashboard widget behavior.\n", encoding="utf-8")

            context_proc = subprocess.run(
                [
                    PY,
                    str(ROOT / "skills" / "context-pack-builder" / "scripts" / "build_context_pack.py"),
                    str(repo),
                    "--request",
                    "dashboard chart widget",
                ],
                text=True,
                capture_output=True,
                check=True,
                timeout=TIMEOUT,
            )
            context = json.loads(context_proc.stdout)
            self.assertIn("src/components/DashboardChart.tsx", {item["path"] for item in context["must_read"]})
            self.assertTrue(context["related_tests"])
            self.assertIn("token_budget", context)
            self.assertTrue(context["token_budget"]["full_doc_requires_reason"])
            self.assertIn("compression_policy", context)

            reuse_proc = subprocess.run(
                [
                    PY,
                    str(ROOT / "skills" / "pattern-reuse-engine" / "scripts" / "find_reuse_candidates.py"),
                    str(repo),
                    "--request",
                    "dashboard chart widget",
                ],
                text=True,
                capture_output=True,
                check=True,
                timeout=TIMEOUT,
            )
            reuse = json.loads(reuse_proc.stdout)
            self.assertIn("DashboardChart", {item["name"] for item in reuse["reuse_candidates"]})
            self.assertTrue(reuse["forbidden_duplicates"])

        gate_proc = subprocess.run(
            [PY, str(ROOT / "skills" / "quality-gate" / "scripts" / "run_quality_gate.py"), str(ROOT / "examples" / "quality-gate-input.json")],
            text=True,
            capture_output=True,
            timeout=TIMEOUT,
        )
        self.assertNotEqual(gate_proc.returncode, 0)
        gate = json.loads(gate_proc.stdout)
        self.assertEqual(gate["status"], "fail")
        gate_types = {item["type"] for item in gate["findings"]}
        self.assertIn("change_budget_exceeded", gate_types)
        self.assertIn("new_file_budget_exceeded", gate_types)

        ready_proc = subprocess.run(
            [PY, str(ROOT / "skills" / "merge-readiness" / "scripts" / "check_merge_readiness.py"), str(ROOT / "examples" / "merge-readiness-input.json")],
            text=True,
            capture_output=True,
            check=True,
            timeout=TIMEOUT,
        )
        ready = json.loads(ready_proc.stdout)
        self.assertEqual(ready["status"], "ready")

        velocity_proc = subprocess.run(
            [
                PY,
                str(ROOT / "skills" / "coding-velocity-report" / "scripts" / "build_velocity_report.py"),
                str(ROOT / "examples" / "velocity-input.json"),
            ],
            text=True,
            capture_output=True,
            check=True,
            timeout=TIMEOUT,
        )
        velocity = json.loads(velocity_proc.stdout)
        self.assertGreaterEqual(velocity["quality_score"], 70)
        self.assertGreaterEqual(velocity["velocity_score"], 70)


if __name__ == "__main__":
    unittest.main(verbosity=2)
