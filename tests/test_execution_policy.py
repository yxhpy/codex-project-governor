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
CHECKER = ROOT / "skills" / "quality-gate" / "scripts" / "check_execution_policy.py"
QUALITY_GATE = ROOT / "skills" / "quality-gate" / "scripts" / "run_quality_gate.py"


class ExecutionPolicyTest(unittest.TestCase):
    def run_payload(self, script: Path, payload: dict, *, check: bool = True) -> tuple[int, dict]:
        with tempfile.NamedTemporaryFile("w+", suffix=".json") as fh:
            json.dump(payload, fh)
            fh.flush()
            proc = subprocess.run(
                [PY, str(script), fh.name],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=check,
                timeout=20,
            )
        return proc.returncode, json.loads(proc.stdout)

    def test_release_publish_blocks_plain_git_push(self) -> None:
        returncode, result = self.run_payload(
            CHECKER,
            {
                "execution_context": "release_publish",
                "commands": ["git push origin main", "git push origin v6.2.4"],
            },
            check=False,
        )
        self.assertNotEqual(returncode, 0)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(result["checked"])
        self.assertIn("execution_command_disallowed", {item["type"] for item in result["findings"]})

    def test_release_publish_accepts_gh_release_or_api(self) -> None:
        returncode, result = self.run_payload(
            CHECKER,
            {
                "execution_context": "release_publish",
                "commands": [
                    "gh api repos/:owner/:repo/git/refs -f ref=refs/tags/v6.2.4 -f sha=abc123",
                    "gh release create v6.2.4 --notes-file releases/6.2.4.md",
                ],
            },
        )
        self.assertEqual(returncode, 0)
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["checked"])
        self.assertEqual(result["summary"]["blocker_count"], 0)

    def test_release_publish_override_turns_blocker_into_warning(self) -> None:
        returncode, result = self.run_payload(
            CHECKER,
            {
                "execution_context": "release_publish",
                "execution_policy_override_approved": True,
                "commands": ["git push origin main"],
            },
        )
        self.assertEqual(returncode, 0)
        self.assertEqual(result["status"], "pass")
        self.assertIn("execution_policy_override_used", {item["type"] for item in result["warnings"]})

    def test_quality_gate_blocks_execution_policy_failure(self) -> None:
        returncode, result = self.run_payload(
            QUALITY_GATE,
            {
                "level": "standard",
                "execution_context": "release_publish",
                "commands": ["git push origin main"],
                "checks": {"selftest": "pass"},
                "allow_no_commands": False,
            },
            check=False,
        )
        self.assertNotEqual(returncode, 0)
        self.assertEqual(result["status"], "fail")
        self.assertIn("execution_policy_failed", {item["type"] for item in result["findings"]})
        self.assertTrue(result["summary"]["execution_policy_checked"])
        self.assertEqual(result["execution_policy"]["context"], "release_publish")


if __name__ == "__main__":
    unittest.main(verbosity=2)
