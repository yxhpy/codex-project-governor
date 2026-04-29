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


class GovernanceArtifactRendererTest(unittest.TestCase):
    def run_json(self, args: list[str]) -> dict:
        proc = subprocess.run(args, text=True, capture_output=True, check=True, timeout=20)
        return json.loads(proc.stdout)

    def write_update_fixture(self, slots: Path, patch: Path) -> None:
        slots.write_text(json.dumps({
            "template_id": "iteration_plan_v1",
            "revision": 1,
            "user_request": "Keep plans mutable.",
            "tests": [],
            "risks": [{"id": "risk-1", "text": "Patch drift.", "status": "open"}]
        }), encoding="utf-8")
        patch.write_text(json.dumps({
            "artifact": "ITERATION_PLAN",
            "base_revision": 1,
            "reason": "Implementation discovered a focused renderer test.",
            "ops": [
                {
                    "op": "append_item",
                    "path": "/tests",
                    "id": "test-1",
                    "value": "python3 tests/test_governance_artifact_renderer.py"
                },
                {
                    "op": "replace_item_field",
                    "path": "/risks",
                    "id": "risk-1",
                    "field": "status",
                    "value": "mitigated"
                }
            ]
        }), encoding="utf-8")

    def test_iteration_plan_slots_render_to_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slots = root / "ITERATION_PLAN.slots.json"
            output = root / "ITERATION_PLAN.md"
            slots.write_text(json.dumps({
                "template_id": "iteration_plan_v1",
                "revision": 1,
                "title": "Iteration Plan",
                "user_request": "Render plans from slots.",
                "existing_behavior": ["Agents write fixed Markdown by hand."],
                "reuse_patterns": [
                    {"pattern": "Deterministic CLI helper", "source": "tools/*.py", "reuse": "Render fixed Markdown."}
                ],
                "expected_changes": [{"path": "tools/render_governance_artifact.py", "reason": "New renderer."}],
                "files_not_to_change": [".codex-plugin/plugin.json"],
                "new_files": [{"file": "tools/render_governance_artifact.py", "why": "No existing renderer."}],
                "tests": ["python3 tests/test_governance_artifact_renderer.py"],
                "risks": [{"id": "risk-1", "text": "Generated Markdown could hide useful context.", "status": "open"}],
                "rollback": "Remove renderer files."
            }), encoding="utf-8")

            result = self.run_json([
                PY,
                str(ROOT / "tools/render_governance_artifact.py"),
                "--input",
                str(slots),
                "--output",
                str(output),
            ])

            self.assertEqual(result["status"], "rendered")
            text = output.read_text(encoding="utf-8")
            self.assertIn("generated_from: iteration_plan_v1", text)
            self.assertIn("Render plans from slots.", text)
            self.assertIn("| Deterministic CLI helper | tools/*.py | Render fixed Markdown. |", text)

    def test_iteration_plan_update_patch_bumps_revision_and_rerenders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slots = root / "ITERATION_PLAN.slots.json"
            patch = root / "ITERATION_PLAN.patch.json"
            markdown = root / "ITERATION_PLAN.md"
            changes = root / "ARTIFACT_CHANGES.jsonl"
            self.write_update_fixture(slots, patch)

            result = self.run_json([
                PY,
                str(ROOT / "tools/update_governance_artifact.py"),
                "--input",
                str(slots),
                "--patch",
                str(patch),
                "--render-output",
                str(markdown),
                "--change-log",
                str(changes),
                "--now",
                "2026-04-30T00:00:00Z",
            ])

            self.assertEqual(result["from_revision"], 1)
            self.assertEqual(result["to_revision"], 2)
            updated = json.loads(slots.read_text(encoding="utf-8"))
            self.assertEqual(updated["revision"], 2)
            self.assertEqual(updated["risks"][0]["status"], "mitigated")
            rendered = markdown.read_text(encoding="utf-8")
            self.assertIn("python3 tests/test_governance_artifact_renderer.py", rendered)
            log_entry = json.loads(changes.read_text(encoding="utf-8").strip())
            self.assertEqual(log_entry["to_revision"], 2)
            self.assertIn("/tests", log_entry["changed_paths"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
