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
CHECKER = ROOT / "skills" / "engineering-standards-governor" / "scripts" / "check_engineering_standards.py"
QUALITY_GATE = ROOT / "skills" / "quality-gate" / "scripts" / "run_quality_gate.py"


class EngineeringStandardsGovernorTest(unittest.TestCase):
    def run_checker(self, project: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [PY, str(CHECKER), "--project", str(project), *extra],
            text=True,
            capture_output=True,
            timeout=20,
        )

    def test_detects_size_complexity_mock_leakage_and_weak_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "tests").mkdir()
            (repo / "src" / "api.ts").write_text(
                "import { user } from '../__mocks__/user';\n"
                "export function handler(value) {\n"
                "  const mockData = user;\n"
                "  if (value) { return mockData; }\n"
                "  return null;\n"
                "}\n",
                encoding="utf-8",
            )
            (repo / "src" / "large.py").write_text("\n".join("# generated line" for _ in range(805)) + "\n", encoding="utf-8")
            complex_lines = ["def decide(value):"]
            for index in range(16):
                complex_lines.append(f"    if value == {index}:")
                complex_lines.append(f"        return {index}")
            complex_lines.append("    return -1")
            (repo / "src" / "complex.py").write_text("\n".join(complex_lines) + "\n", encoding="utf-8")
            (repo / "tests" / "api.test.ts").write_text("test('loads', () => { handler(1); });\n", encoding="utf-8")

            proc = self.run_checker(repo)

            self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["schema"], "project-governor-engineering-standards-v1")
            self.assertEqual(data["status"], "fail")
            types = {item["type"] for item in data["findings"]}
            self.assertIn("source_file_too_large", types)
            self.assertIn("function_too_complex", types)
            self.assertIn("production_mock_import", types)
            self.assertIn("mock_like_production_data", types)
            self.assertIn("test_without_assertions", types)
            self.assertGreaterEqual(data["summary"]["mock_inventory_count"], 2)

    def test_healthy_project_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "tests").mkdir()
            (repo / "src" / "service.ts").write_text(
                "export function loadCount(items) {\n"
                "  if (!items) { return 0; }\n"
                "  return items.length;\n"
                "}\n",
                encoding="utf-8",
            )
            (repo / "tests" / "service.test.ts").write_text(
                "test('loads count', () => { expect(loadCount([1])).toEqual(1); });\n",
                encoding="utf-8",
            )

            proc = self.run_checker(repo)

            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["status"], "pass")
            self.assertEqual(data["summary"]["blocker_count"], 0)

    def test_diff_scope_suppresses_existing_baseline_debt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            legacy = ["def legacy(value):"]
            for index in range(20):
                legacy.append(f"    if value == {index}:")
                legacy.append(f"        return {index}")
            legacy.append("    return -1")
            (repo / "src" / "legacy.py").write_text("\n".join(legacy) + "\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "init"], text=True, capture_output=True, check=True, timeout=20)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True, timeout=20)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Project Governor Test"], check=True, timeout=20)
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True, timeout=20)
            subprocess.run(["git", "-C", str(repo), "commit", "-m", "baseline"], text=True, capture_output=True, check=True, timeout=20)
            updated = (repo / "src" / "legacy.py").read_text(encoding="utf-8").replace("return -1", "return 0")
            (repo / "src" / "legacy.py").write_text(updated, encoding="utf-8")

            proc = self.run_checker(repo, "--diff-base", "HEAD")

            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["status"], "pass")
            self.assertGreater(data["summary"]["suppressed_baseline_count"], 0)

    def test_quality_gate_consumes_engineering_standards_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "quality.json"
            input_path.write_text(
                json.dumps(
                    {
                        "level": "standard",
                        "commands": ["python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project ."],
                        "engineering_standards": {
                            "status": "fail",
                            "summary": {"blocker_count": 1, "warning_count": 2},
                        },
                    }
                ),
                encoding="utf-8",
            )

            proc = subprocess.run([PY, str(QUALITY_GATE), str(input_path)], text=True, capture_output=True, timeout=20)

            self.assertNotEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            self.assertEqual(data["status"], "fail")
            self.assertIn("engineering_standards_failed", {item["type"] for item in data["findings"]})

    def test_strict_quality_gate_blocks_engineering_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "quality.json"
            input_path.write_text(
                json.dumps(
                    {
                        "level": "strict",
                        "commands": ["python3 skills/engineering-standards-governor/scripts/check_engineering_standards.py --project ."],
                        "engineering_standards": {
                            "status": "warn",
                            "summary": {"blocker_count": 0, "warning_count": 1},
                        },
                    }
                ),
                encoding="utf-8",
            )

            proc = subprocess.run([PY, str(QUALITY_GATE), str(input_path)], text=True, capture_output=True, timeout=20)

            self.assertNotEqual(proc.returncode, 0)
            data = json.loads(proc.stdout)
            self.assertEqual(data["status"], "fail")
            self.assertIn("engineering_standards_warnings", {item["type"] for item in data["blockers"]})


if __name__ == "__main__":
    unittest.main(verbosity=2)
