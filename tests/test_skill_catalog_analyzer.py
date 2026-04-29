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
ANALYZER = ROOT / "tools/analyze_skill_catalog.py"


class SkillCatalogAnalyzerTest(unittest.TestCase):
    def run_cmd(self, args: list[str], expect_success: bool = True) -> subprocess.CompletedProcess[str]:
        proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=20)
        if expect_success:
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        return proc

    def run_json(self, args: list[str], expect_success: bool = True) -> dict:
        proc = self.run_cmd(args, expect_success=expect_success)
        return json.loads(proc.stdout)

    def test_current_catalog_reports_health_and_candidates(self) -> None:
        data = self.run_json([PY, str(ANALYZER), "--project", str(ROOT), "--fail-on-issues"])
        self.assertEqual(data["schema"], "project-governor-skill-catalog-analysis-v1")
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["skill_count"], data["catalog_entry_count"])
        self.assertGreaterEqual(data["skill_count"], 35)
        self.assertEqual(data["issues"], [])
        self.assertEqual(data["summary"]["candidate_count"], 0)
        self.assertGreater(data["summary"]["resolved_consolidation_count"], 0)
        self.assertIn("primary", data["visibility_counts"])
        self.assertIn("internal", data["visibility_counts"])
        self.assertIn("workflow", data["visibility_counts"])
        self.assertIn("quality", data["category_counts"])
        resolved_types = {item["type"] for item in data["resolved_consolidations"]}
        self.assertIn("quality_gate_facets", resolved_types)

    def test_current_catalog_reports_resolved_consolidations_separately(self) -> None:
        data = self.run_json([PY, str(ANALYZER), "--project", str(ROOT)])
        resolved_by = {item["resolved_by"] for item in data["resolved_consolidations"]}
        self.assertIn("initialization-entrypoint", resolved_by)
        self.assertIn("maintenance-entrypoint", resolved_by)
        self.assertIn("evidence-upgrade-entrypoint", resolved_by)
        self.assertIn("quality-entrypoint", resolved_by)
        self.assertEqual(data["consolidation_candidates"], [])

    def test_analyzer_files_stay_below_engineering_warning_threshold(self) -> None:
        for rel_path in [
            "tools/analyze_skill_catalog.py",
            "tools/skill_catalog_analysis.py",
            "tools/skill_catalog_render.py",
            "tools/skill_catalog_validation.py",
        ]:
            line_count = len((ROOT / rel_path).read_text(encoding="utf-8").splitlines())
            self.assertLessEqual(line_count, 400, rel_path)

    def test_current_readme_groups_follow_catalog_visibility(self) -> None:
        data = self.run_json([PY, str(ANALYZER), "--project", str(ROOT)])
        catalog = json.loads((ROOT / "skills/CATALOG.json").read_text(encoding="utf-8"))
        by_name = {entry["name"]: entry for entry in catalog["skills"]}
        self.assertEqual(by_name["design-md-aesthetic-governor"]["visibility"], "advanced")
        self.assertEqual(by_name["version-researcher"]["visibility"], "advanced")
        self.assertEqual(data["issues"], [])

    def test_readme_initialization_entry_is_consolidated(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        zh_readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        self.assertIn("Initialization: `init-empty-project` / `init-existing-project`", readme)
        self.assertIn("初始化：`init-empty-project` / `init-existing-project`", zh_readme)
        self.assertNotIn("| `init-empty-project` |", readme)
        self.assertNotIn("| `init-existing-project` |", readme)

    def test_readme_maintenance_entry_is_consolidated(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        zh_readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        self.assertIn("Maintenance: `clean-reinstall-manager` / `plugin-upgrade-migrator`", readme)
        self.assertIn("维护：`clean-reinstall-manager` / `plugin-upgrade-migrator`", zh_readme)
        self.assertNotIn("| `clean-reinstall-manager` |", readme)
        self.assertNotIn("| `plugin-upgrade-migrator` |", readme)

    def test_readme_evidence_upgrade_entry_is_consolidated(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        zh_readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        self.assertIn("Evidence and upgrades: `research-radar` / `upgrade-advisor`", readme)
        self.assertIn("证据和升级：`research-radar` / `upgrade-advisor`", zh_readme)
        self.assertNotIn("| `research-radar` |", readme)
        self.assertNotIn("| `upgrade-advisor` |", readme)

    def test_text_output_includes_status_and_candidates(self) -> None:
        proc = self.run_cmd([PY, str(ANALYZER), "--project", str(ROOT), "--format", "text"])
        self.assertIn("status: pass", proc.stdout)
        self.assertIn("resolved consolidations:", proc.stdout)
        self.assertIn("consolidation candidates:", proc.stdout)
        self.assertIn("quality_gate_facets", proc.stdout)
        self.assertIn("- none", proc.stdout)

    def test_fail_on_issues_detects_missing_catalog_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "skills/example").mkdir(parents=True)
            (project / "skills/example/SKILL.md").write_text(
                "---\nname: example\ndescription: Example skill used by analyzer tests.\n---\n",
                encoding="utf-8",
            )
            (project / "skills/CATALOG.json").write_text(
                json.dumps(
                    {
                        "schema": "project-governor-skill-catalog-v1",
                        "description": "Test catalog.",
                        "visibility_values": ["primary", "workflow", "internal", "advanced", "deprecated"],
                        "skills": [],
                    }
                ),
                encoding="utf-8",
            )

            data = self.run_json([PY, str(ANALYZER), "--project", str(project), "--fail-on-issues"], expect_success=False)
            self.assertEqual(data["status"], "fail")
            self.assertIn("missing_catalog_entry", {item["type"] for item in data["issues"]})

    def test_missing_catalog_file_returns_structured_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "skills/example").mkdir(parents=True)
            (project / "skills/example/SKILL.md").write_text(
                "---\nname: example\ndescription: Example skill used by analyzer tests.\n---\n",
                encoding="utf-8",
            )

            data = self.run_json([PY, str(ANALYZER), "--project", str(project), "--fail-on-issues"], expect_success=False)
            issue_types = {item["type"] for item in data["issues"]}
            self.assertEqual(data["status"], "fail")
            self.assertIn("missing_catalog_file", issue_types)
            self.assertIn("missing_catalog_entry", issue_types)

    def test_readme_skill_group_drift_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            for name in ["example-primary", "example-internal", "example-advanced"]:
                (project / "skills" / name).mkdir(parents=True)
                (project / "skills" / name / "SKILL.md").write_text(
                    f"---\nname: {name}\ndescription: Example skill used by analyzer tests.\n---\n",
                    encoding="utf-8",
                )
            (project / "skills/CATALOG.json").write_text(
                json.dumps(
                    {
                        "schema": "project-governor-skill-catalog-v1",
                        "description": "Test catalog.",
                        "visibility_values": ["primary", "workflow", "internal", "advanced", "deprecated"],
                        "skills": [
                            {
                                "name": "example-primary",
                                "visibility": "primary",
                                "category": "orchestration",
                                "summary": "Primary example skill for README drift tests.",
                            },
                            {
                                "name": "example-internal",
                                "visibility": "internal",
                                "category": "context",
                                "summary": "Internal example skill for README drift tests.",
                            },
                            {
                                "name": "example-advanced",
                                "visibility": "advanced",
                                "category": "quality",
                                "summary": "Advanced example skill for README drift tests.",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (project / "README.md").write_text(
                """## Skills

### Recommended entry points

| Skill | Use when |
|---|---|
| `example-internal` | Wrong group. |

### Internal workflow stages

These skills normally run internally: `example-primary`.

### Advanced and diagnostic tools

Use these directly only for diagnostics: `example-advanced`.

## Install locally for yourself
""",
                encoding="utf-8",
            )
            (project / "README.zh-CN.md").write_text(
                """## 技能入口

### 推荐入口

| Skill | 适用场景 |
|---|---|
| `example-primary` | 正确分组。 |

### 内部工作流阶段

这些技能通常自动调用：`example-internal`。

### 高级和诊断工具

只有在需要诊断时才直接使用：`example-advanced`。

## 安装到个人 Codex
""",
                encoding="utf-8",
            )

            data = self.run_json([PY, str(ANALYZER), "--project", str(project), "--fail-on-issues"], expect_success=False)
            issue_types = {item["type"] for item in data["issues"]}
            self.assertEqual(data["status"], "fail")
            self.assertIn("readme_skill_group_missing", issue_types)
            self.assertIn("readme_skill_group_extra", issue_types)

    def test_unknown_consolidation_group_skill_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            for name in ["example-primary", "example-workflow"]:
                (project / "skills" / name).mkdir(parents=True)
                (project / "skills" / name / "SKILL.md").write_text(
                    f"---\nname: {name}\ndescription: Example skill used by analyzer tests.\n---\n",
                    encoding="utf-8",
                )
            (project / "skills/CATALOG.json").write_text(
                json.dumps(
                    {
                        "schema": "project-governor-skill-catalog-v1",
                        "description": "Test catalog.",
                        "visibility_values": ["primary", "workflow", "internal", "advanced", "deprecated"],
                        "consolidation_groups": [
                            {
                                "name": "broken-group",
                                "status": "resolved",
                                "skills": ["example-primary", "missing-skill"],
                            }
                        ],
                        "skills": [
                            {
                                "name": "example-primary",
                                "visibility": "primary",
                                "category": "orchestration",
                                "summary": "Primary example skill for consolidation group tests.",
                            },
                            {
                                "name": "example-workflow",
                                "visibility": "workflow",
                                "category": "orchestration",
                                "summary": "Workflow example skill for consolidation group tests.",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            for rel_path, headings in {
                "README.md": ("### Recommended entry points", "### Internal workflow stages", "### Advanced and diagnostic tools", "## Install locally for yourself"),
                "README.zh-CN.md": ("### 推荐入口", "### 内部工作流阶段", "### 高级和诊断工具", "## 安装到个人 Codex"),
            }.items():
                recommended, internal, advanced, end = headings
                (project / rel_path).write_text(
                    f"""## Skills

{recommended}

`example-primary` `example-workflow`

{internal}

No internal skills.

{advanced}

No advanced skills.

{end}
""",
                    encoding="utf-8",
                )

            data = self.run_json([PY, str(ANALYZER), "--project", str(project), "--fail-on-issues"], expect_success=False)
            self.assertEqual(data["status"], "fail")
            self.assertIn("unknown_consolidation_group_skill", {item["type"] for item in data["issues"]})


if __name__ == "__main__":
    unittest.main(verbosity=2)
