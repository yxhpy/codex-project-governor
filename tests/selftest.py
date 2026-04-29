#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from selftest_helpers import (
    ALLOWED_CATEGORIES,
    ALLOWED_VISIBILITY,
    MANAGED_ASSET_PATHS,
    PY,
    REQUIRED_SKILLS,
    REQUIRED_TEMPLATE_PATHS,
    ROOT,
    TIMEOUT,
    assert_acceleration_tools,
)


class ProjectGovernorSelfTest(unittest.TestCase):
    def test_plugin_manifest(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "codex-project-governor")
        self.assertEqual(manifest["version"], "6.2.2")
        self.assertIn("Harness v6.2.2", manifest["description"])
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertIn("interface", manifest)
        self.assertIn("defaultPrompt", manifest["interface"])
        default_prompts = manifest["interface"]["defaultPrompt"]
        self.assertIsInstance(default_prompts, list)
        self.assertLessEqual(len(default_prompts), 8)
        self.assertGreaterEqual(len(default_prompts), 5)
        joined_prompts = "\n".join(default_prompts)
        for expected in ["initialize", "upgrade", "memory", "DESIGN.md", "PR-ready"]:
            self.assertIn(expected, joined_prompts)
        for internal_skill in {
            "task-router",
            "context-indexer",
            "session-lifecycle",
            "evidence-manifest",
            "route-guard",
            "engineering-standards-governor",
            "gpt55-auto-orchestrator",
            "design-md-aesthetic-governor",
        }:
            self.assertNotIn(internal_skill, joined_prompts)
        feature_matrix = json.loads((ROOT / "releases" / "FEATURE_MATRIX.json").read_text(encoding="utf-8"))
        self.assertEqual(feature_matrix["current_latest"], "6.2.2")
        versions = {item["version"] for item in feature_matrix["versions"]}
        self.assertIn("6.2.2", versions)
        self.assertTrue((ROOT / "releases" / "6.2.2.md").exists())

    def test_skills_have_metadata(self) -> None:
        skill_dirs = [p for p in (ROOT / "skills").iterdir() if p.is_dir()]
        self.assertGreaterEqual(len(skill_dirs), 35)
        names = {p.name for p in skill_dirs}
        for required in REQUIRED_SKILLS:
            self.assertIn(required, names)
        for skill_dir in skill_dirs:
            skill_md = skill_dir / "SKILL.md"
            self.assertTrue(skill_md.exists(), skill_dir)
            text = skill_md.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), skill_md)
            self.assertIn("name:", text)
            self.assertIn("description:", text)

    def test_skill_catalog_matches_skill_dirs(self) -> None:
        catalog = json.loads((ROOT / "skills" / "CATALOG.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["schema"], "project-governor-skill-catalog-v1")
        actual_names = {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()}
        entries = catalog.get("skills", [])
        catalog_names = [entry.get("name") for entry in entries]
        self.assertEqual(len(catalog_names), len(set(catalog_names)))
        self.assertEqual(set(catalog_names), actual_names)

        primary = [entry for entry in entries if entry.get("visibility") == "primary"]
        self.assertGreaterEqual(len(primary), 1)
        for entry in entries:
            self.assertIn(entry.get("visibility"), ALLOWED_VISIBILITY, entry)
            self.assertIn(entry.get("category"), ALLOWED_CATEGORIES, entry)
            self.assertIsInstance(entry.get("summary"), str, entry)
            self.assertGreater(len(entry.get("summary", "")), 20, entry)

    def test_required_templates_exist(self) -> None:
        for rel in REQUIRED_TEMPLATE_PATHS:
            self.assertTrue((ROOT / "templates" / rel).exists(), rel)

    def test_managed_assets_exist(self) -> None:
        for rel in MANAGED_ASSET_PATHS:
            self.assertTrue((ROOT / "managed-assets" / rel).exists(), rel)

    def test_chinese_docs_exist(self) -> None:
        readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        usage = (ROOT / "docs" / "zh-CN" / "USAGE.md").read_text(encoding="utf-8")
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("README.zh-CN.md", english)
        self.assertIn("Project Governor", readme)
        self.assertIn("research-radar", readme)
        self.assertIn("version-researcher", readme)
        self.assertIn("6.2.2", readme)
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
        assert_acceleration_tools(self)


if __name__ == "__main__":
    unittest.main(verbosity=2)
