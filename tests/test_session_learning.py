#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


class SessionLearningTest(unittest.TestCase):
    def run_json(self, args: list[str]) -> dict:
        proc = subprocess.run(args, text=True, capture_output=True, check=True, timeout=20)
        return json.loads(proc.stdout)

    def prepare_learning_project(self, project: Path) -> None:
        (project / ".project-governor").mkdir()
        (project / "docs" / "memory").mkdir(parents=True)
        (project / "docs" / "memory" / "REPEATED_AGENT_MISTAKES.md").write_text(
            "# Repeated Agent Mistakes\n\n"
            "| Date | Mistake | Correct behavior | Evidence | Encoded where | Status |\n"
            "|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )

    def write_learning_payload(self, project: Path) -> Path:
        payload = {
            "task_id": "demo-learning",
            "source": "test_session_learning",
            "items": [
                {
                    "type": "command_failure",
                    "command": "git push origin main && git push origin v6.0.4",
                    "error": "approval required by policy",
                    "lesson": "Use GitHub API fallback when git push is blocked by the runtime policy.",
                    "evidence": "failed push in release workflow",
                },
                {
                    "type": "command_failure",
                    "command": "python3 missing-script.py",
                    "error": "No such file or directory",
                    "lesson": "Check rg --files before running remembered script paths.",
                    "repeat_count": 2,
                    "evidence": "same missing script path repeated",
                },
                {"type": "stale_memory", "memory": "Old release says latest is v6.0.3", "path": "docs/memory/PROJECT_MEMORY.md", "reason": "v6.0.4 superseded it"},
                {"type": "command_failure", "command": "curl -H 'Authorization: token ghp_secretsecretsecretsecret' https://example.invalid", "error": "401"},
            ],
        }
        input_path = project / "learning.json"
        input_path.write_text(json.dumps(payload), encoding="utf-8")
        return input_path

    def record_learning(self, project: Path, input_path: Path) -> dict:
        return self.run_json([
            PY,
            str(ROOT / "skills" / "memory-compact" / "scripts" / "record_session_learning.py"),
            "--project",
            str(project),
            "--input",
            str(input_path),
            "--apply",
        ])

    def assert_learning_layers(self, project: Path, result: dict) -> None:
        self.assertEqual(result["status"], "applied")
        classifications = [item["classification"] for item in result["results"]]
        self.assertIn("command_learning", classifications)
        self.assertIn("repeated_mistake", classifications)
        self.assertIn("stale_memory", classifications)
        self.assertIn("secret_or_sensitive", classifications)

        command_state = json.loads((project / ".project-governor" / "state" / "COMMAND_LEARNINGS.json").read_text(encoding="utf-8"))
        self.assertEqual(command_state["schema"], "project-governor-command-learnings-v1")
        self.assertEqual(len(command_state["learnings"]), 2)
        self.assertIn("approval required", json.dumps(command_state))
        self.assertNotIn("ghp_secretsecretsecretsecret", json.dumps(command_state))

        hygiene_state = json.loads((project / ".project-governor" / "state" / "MEMORY_HYGIENE.json").read_text(encoding="utf-8"))
        self.assertEqual(hygiene_state["schema"], "project-governor-memory-hygiene-v1")
        self.assertEqual(len(hygiene_state["items"]), 1)

        repeated = (project / "docs" / "memory" / "REPEATED_AGENT_MISTAKES.md").read_text(encoding="utf-8")
        self.assertIn("missing-script.py", repeated)

    def assert_memory_search_finds_learning(self, project: Path) -> None:
        search = self.run_json([
            PY,
            str(ROOT / "skills" / "context-indexer" / "scripts" / "query_context_index.py"),
            "--project",
            str(project),
            "--request",
            "git push approval required missing script stale latest",
            "--memory-search",
            "--auto-build",
        ])
        paths = {item["path"] for item in search["recommended_files"]}
        self.assertIn(".project-governor/state/COMMAND_LEARNINGS.json", paths)
        self.assertIn(".project-governor/state/MEMORY_HYGIENE.json", paths)

    def test_record_session_learning_layers_and_memory_search(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.prepare_learning_project(project)
            result = self.record_learning(project, self.write_learning_payload(project))
            self.assert_learning_layers(project, result)
            self.assert_memory_search_finds_learning(project)

    def test_orchestrator_requires_memory_learning_for_standard_routes(self) -> None:
        data = self.run_json([
            PY,
            str(ROOT / "skills" / "gpt55-auto-orchestrator" / "scripts" / "select_runtime_plan.py"),
            "--request",
            "Fix export command regression with tests",
        ])
        self.assertTrue(data["context_retrieval"]["startup_memory_search"])
        self.assertTrue(data["memory_policy"]["startup_memory_search_required"])
        self.assertTrue(data["memory_policy"]["record_session_learning_required"])
        self.assertEqual(data["memory_policy"]["failed_commands_target"], ".project-governor/state/COMMAND_LEARNINGS.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
