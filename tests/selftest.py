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


class ProjectGovernorSelfTest(unittest.TestCase):
    def test_plugin_manifest(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "codex-project-governor")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertIn("interface", manifest)
        self.assertIn("defaultPrompt", manifest["interface"])

    def test_skills_have_metadata(self) -> None:
        skill_dirs = [p for p in (ROOT / "skills").iterdir() if p.is_dir()]
        self.assertGreaterEqual(len(skill_dirs), 10)
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
            "docs/project/CHARTER.md",
            "docs/conventions/ITERATION_CONTRACT.md",
            "docs/conventions/CONVENTION_MANIFEST.md",
            "docs/architecture/ARCHITECTURE.md",
            "docs/memory/PROJECT_MEMORY.md",
            "docs/memory/OPEN_QUESTIONS.md",
            "docs/decisions/ADR-0000-template.md",
            "tasks/_template/ITERATION_PLAN.md",
            ".codex/prompts/memory-compact.md",
            ".codex/hooks/check_iteration_compliance.py",
        ]
        for rel in required:
            self.assertTrue((ROOT / "templates" / rel).exists(), rel)

    def test_project_rules_use_valid_decisions(self) -> None:
        rules = (ROOT / "templates" / ".codex" / "rules" / "project.rules").read_text(encoding="utf-8")
        decisions = re.findall(r'decision="([^"]+)"', rules)
        self.assertGreater(len(decisions), 0)
        self.assertEqual(set(decisions) - {"allow", "deny", "prompt"}, set())

    def test_init_project_preserves_application_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            source = repo / "src" / "main.ts"
            package_json = repo / "package.json"
            source.write_text("export const x = 1;\n", encoding="utf-8")
            package_json.write_text('{"name":"fixture"}\n', encoding="utf-8")
            subprocess.check_call([PY, str(ROOT / "tools" / "init_project.py"), "--mode", "existing", "--target", str(repo), "--json"])
            self.assertEqual(source.read_text(encoding="utf-8"), "export const x = 1;\n")
            self.assertEqual(package_json.read_text(encoding="utf-8"), '{"name":"fixture"}\n')
            self.assertTrue((repo / "AGENTS.md").exists())
            self.assertTrue((repo / "docs" / "conventions" / "ITERATION_CONTRACT.md").exists())

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
