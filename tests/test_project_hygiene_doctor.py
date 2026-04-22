#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
SCRIPT = ROOT / "skills" / "project-hygiene-doctor" / "scripts" / "inspect_project_hygiene.py"
INIT = ROOT / "tools" / "init_project.py"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ProjectHygieneDoctorTest(unittest.TestCase):
    def run_doctor(self, project: Path, *extra: str, plugin_root: Path | None = ROOT) -> tuple[int, dict]:
        command = [PY, str(SCRIPT), "--project", str(project)]
        if plugin_root:
            command.extend(["--plugin-root", str(plugin_root)])
        command.extend(extra)
        process = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=15,
        )
        return process.returncode, json.loads(process.stdout)

    def test_generated_global_agent_is_safe_to_quarantine(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            content = 'name = "context-scout"\nmodel = "gpt-5.4-mini"\n'
            agent = project / ".codex" / "agents" / "context-scout.toml"
            agent.parent.mkdir(parents=True)
            agent.write_text(content, encoding="utf-8")
            manifest = project / ".project-governor" / "INSTALL_MANIFEST.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                json.dumps(
                    {
                        "generated_files": [
                            {
                                "path": ".codex/agents/context-scout.toml",
                                "installed_sha256": sha(content),
                                "upgrade_policy": "generated_global_asset",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            code, report = self.run_doctor(project)
            self.assertEqual(code, 2)
            self.assertEqual(report["summary"]["safe_to_quarantine_count"], 1)

            code, applied = self.run_doctor(project, "--apply")
            self.assertEqual(code, 0)
            self.assertFalse(agent.exists())
            self.assertEqual(applied["summary"]["applied_count"], 1)
            self.assertEqual(len(list((project / ".project-governor" / "hygiene-quarantine").rglob("context-scout.toml"))), 1)

    def test_untracked_codex_asset_requires_manual_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            custom = project / ".codex" / "agents" / "custom.toml"
            custom.parent.mkdir(parents=True)
            custom.write_text('name = "custom"\n', encoding="utf-8")

            code, report = self.run_doctor(project)
            self.assertEqual(code, 2)
            self.assertEqual(report["status"], "needs_manual_review")
            self.assertTrue(custom.exists())

    def test_memory_and_decisions_are_protected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            memory = project / "docs" / "memory" / "PROJECT_MEMORY.md"
            decision = project / "docs" / "decisions" / "ADR.md"
            memory.parent.mkdir(parents=True)
            decision.parent.mkdir(parents=True)
            memory.write_text("# Memory\n", encoding="utf-8")
            decision.write_text("# ADR\n", encoding="utf-8")

            _, report = self.run_doctor(project)
            actions = {item["path"]: item["action"] for item in report["findings"]}
            self.assertEqual(actions["docs/memory/PROJECT_MEMORY.md"], "never_touch")
            self.assertEqual(actions["docs/decisions/ADR.md"], "never_touch")

    def test_plugin_repo_source_is_not_flagged_as_leak(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            manifest = project / ".codex-plugin" / "plugin.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"name": "codex-project-governor"}), encoding="utf-8")
            skill = project / "skills" / "x" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: x\n---\n", encoding="utf-8")
            agent = project / ".codex" / "agents" / "context-scout.toml"
            prompt = project / ".codex" / "prompts" / "memory-compact.md"
            config = project / ".codex" / "config.toml"
            agent.parent.mkdir(parents=True)
            prompt.parent.mkdir(parents=True)
            agent.write_text('name = "context-scout"\n', encoding="utf-8")
            prompt.write_text("Use memory compact.\n", encoding="utf-8")
            config.write_text("[project]\n", encoding="utf-8")

            code, report = self.run_doctor(project, plugin_root=project)
            self.assertEqual(code, 0)
            self.assertEqual(report["status"], "clean")
            classifications = {item["path"]: item["classification"] for item in report["findings"]}
            self.assertEqual(classifications["skills/x/SKILL.md"], "plugin_repo_source")
            self.assertEqual(classifications[".codex/agents/context-scout.toml"], "plugin_repo_runtime_asset")
            self.assertEqual(classifications[".codex/prompts/memory-compact.md"], "plugin_repo_runtime_asset")
            self.assertEqual(classifications[".codex/config.toml"], "plugin_repo_runtime_asset")

    def test_copied_plugin_source_is_flagged_when_project_is_not_plugin_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            manifest = project / ".codex-plugin" / "plugin.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"name": "codex-project-governor"}), encoding="utf-8")
            skill = project / "skills" / "x" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: x\n---\n", encoding="utf-8")

            code, report = self.run_doctor(project)
            self.assertEqual(code, 2)
            self.assertEqual(report["status"], "needs_manual_review")
            classifications = {item["path"]: item["classification"] for item in report["findings"]}
            self.assertEqual(classifications[".codex-plugin/plugin.json"], "plugin_source_leak")
            self.assertEqual(classifications["skills/x/SKILL.md"], "plugin_source_leak")

    def test_common_project_tests_are_not_flagged_as_plugin_leaks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            test_file = project / "tests" / "test_app.py"
            test_file.parent.mkdir()
            test_file.write_text("def test_app():\n    assert True\n", encoding="utf-8")

            code, report = self.run_doctor(project)
            self.assertEqual(code, 0)
            self.assertEqual(report["status"], "clean")

    def test_clean_init_skips_global_codex_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            process = subprocess.run(
                [PY, str(INIT), "--target", str(project), "--mode", "existing", "--json"],
                text=True,
                capture_output=True,
                check=True,
                timeout=15,
            )
            result = json.loads(process.stdout)
            self.assertEqual(result["profile"], "clean")
            self.assertIn("AGENTS.md", set(result["created"]))
            self.assertFalse((project / ".codex" / "agents").exists())
            self.assertTrue((project / ".codex" / "rules" / "project.rules").exists())
            self.assertTrue((project / ".codex" / "hooks" / "check_iteration_compliance.py").exists())
            self.assertTrue((project / ".codex" / "hooks.json").exists())
            self.assertIn(".codex/config.toml", set(result["skipped_global"]))
            self.assertIn(".codex/config.toml", set(result["skipped"]))

    def test_legacy_full_init_copies_codex_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            process = subprocess.run(
                [PY, str(INIT), "--target", str(project), "--mode", "existing", "--profile", "legacy-full", "--json"],
                text=True,
                capture_output=True,
                check=True,
                timeout=15,
            )
            result = json.loads(process.stdout)
            self.assertEqual(result["profile"], "legacy-full")
            self.assertTrue((project / ".codex" / "agents").exists())
            self.assertIn(".project-governor/INSTALL_MANIFEST.json", set(result["created"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
