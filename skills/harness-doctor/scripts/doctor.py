#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import py_compile
from pathlib import Path
from typing import Any

REQUIRED_SKILLS = {
    "task-router",
    "gpt55-auto-orchestrator",
    "context-indexer",
    "context-pack-builder",
    "route-guard",
    "engineering-standards-governor",
    "quality-gate",
    "merge-readiness",
    "session-lifecycle",
    "evidence-manifest",
    "harness-doctor",
}
REQUIRED_STATE_FILES = ["FEATURES.json", "AGENTS.json", "ISSUES.json", "PROGRESS.md", "SESSION.json"]
REQUIRED_SCRIPT_PATHS = [
    "skills/task-router/scripts/classify_task.py",
    "skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py",
    "skills/context-indexer/scripts/build_context_index.py",
    "skills/context-indexer/scripts/query_context_index.py",
    "skills/route-guard/scripts/check_route_guard.py",
    "skills/route-guard/scripts/collect_diff_facts.py",
    "skills/quality-gate/scripts/run_quality_gate.py",
    "skills/merge-readiness/scripts/check_merge_readiness.py",
    "skills/session-lifecycle/scripts/session_lifecycle.py",
    "skills/evidence-manifest/scripts/write_evidence_manifest.py",
]


def check_file(path: Path, label: str, blockers: list[str], warnings: list[str]) -> None:
    if not path.exists():
        blockers.append(f"missing {label}: {path}")


def compile_script(path: Path, blockers: list[str]) -> None:
    if not path.exists():
        blockers.append(f"missing script: {path}")
        return
    try:
        py_compile.compile(str(path), doraise=True)
    except Exception as exc:
        blockers.append(f"python compile failed for {path}: {exc}")


def expected_manifest_version(project: Path, warnings: list[str]) -> str | None:
    matrix_path = project / "releases" / "FEATURE_MATRIX.json"
    if not matrix_path.exists():
        return None
    try:
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    except Exception as exc:
        warnings.append(f"release feature matrix is invalid JSON: {exc}")
        return None
    version = matrix.get("current_latest")
    return version if isinstance(version, str) and version else None


def check_manifest(project: Path, blockers: list[str], warnings: list[str]) -> None:
    manifest_path = project / ".codex-plugin" / "plugin.json"
    check_file(manifest_path, "plugin manifest", blockers, warnings)
    expected_version = expected_manifest_version(project, warnings)
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if expected_version and manifest.get("version") != expected_version:
                warnings.append(f"manifest version is {manifest.get('version')}, expected {expected_version}")
        except Exception as exc:
            blockers.append(f"plugin manifest is invalid JSON: {exc}")


def check_skills(project: Path, blockers: list[str], warnings: list[str]) -> None:
    skills_dir = project / "skills"
    check_file(skills_dir, "skills directory", blockers, warnings)
    if not skills_dir.exists():
        return
    names = {p.name for p in skills_dir.iterdir() if p.is_dir()}
    missing = sorted(REQUIRED_SKILLS - names)
    if missing:
        blockers.append(f"missing required Harness v6 skills: {missing}")
    for skill in names:
        if not (skills_dir / skill / "SKILL.md").exists():
            blockers.append(f"skill missing SKILL.md: {skill}")


def check_json_schema(path: Path, label: str, expected_schema: str, blockers: list[str], warnings: list[str]) -> None:
    if not path.exists():
        warnings.append(f"{label} is missing; run context-indexer --write")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        blockers.append(f"{label} invalid JSON: {exc}")
        return
    if data.get("schema") != expected_schema:
        warnings.append(f"{label} schema is {data.get('schema')}, expected {expected_schema}")


def check_context_outputs(project: Path, blockers: list[str], warnings: list[str]) -> None:
    context = project / ".project-governor" / "context"
    check_json_schema(context / "CONTEXT_INDEX.json", "context index", "project-governor-context-index-v2", blockers, warnings)
    check_json_schema(context / "DOCS_MANIFEST.json", "docs manifest", "project-governor-docs-manifest-v1", blockers, warnings)


def check_state_files(project: Path, warnings: list[str]) -> None:
    state = project / ".project-governor" / "state"
    for rel in REQUIRED_STATE_FILES:
        if not (state / rel).exists():
            warnings.append(f"state file missing: .project-governor/state/{rel}")


def compile_required_scripts(project: Path, execution_readiness: bool, blockers: list[str], warnings: list[str]) -> None:
    target = blockers if execution_readiness else warnings
    for rel in REQUIRED_SCRIPT_PATHS:
        compile_script(project / rel, target)


def diagnose(project: Path, execution_readiness: bool = False) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    check_manifest(project, blockers, warnings)
    check_skills(project, blockers, warnings)
    check_context_outputs(project, blockers, warnings)
    check_state_files(project, warnings)
    compile_required_scripts(project, execution_readiness, blockers, warnings)
    status = "fail" if blockers else "pass"
    return {
        "status": status,
        "schema": "project-governor-harness-doctor-v1",
        "project": str(project),
        "execution_readiness": execution_readiness,
        "blockers": blockers,
        "warnings": warnings,
        "summary": {"blocker_count": len(blockers), "warning_count": len(warnings)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose Project Governor Harness v6 install and execution readiness.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--execution-readiness", action="store_true")
    args = parser.parse_args()
    result = diagnose(args.project.resolve(), args.execution_readiness)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
