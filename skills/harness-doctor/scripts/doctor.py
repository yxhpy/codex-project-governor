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


def diagnose(project: Path, execution_readiness: bool = False) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    manifest_path = project / ".codex-plugin" / "plugin.json"
    check_file(manifest_path, "plugin manifest", blockers, warnings)
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("version") != "6.1.0":
                warnings.append(f"manifest version is {manifest.get('version')}, expected 6.1.0")
        except Exception as exc:
            blockers.append(f"plugin manifest is invalid JSON: {exc}")
    skills_dir = project / "skills"
    check_file(skills_dir, "skills directory", blockers, warnings)
    if skills_dir.exists():
        names = {p.name for p in skills_dir.iterdir() if p.is_dir()}
        missing = sorted(REQUIRED_SKILLS - names)
        if missing:
            blockers.append(f"missing required Harness v6 skills: {missing}")
        for skill in names:
            if not (skills_dir / skill / "SKILL.md").exists():
                blockers.append(f"skill missing SKILL.md: {skill}")
    index = project / ".project-governor" / "context" / "CONTEXT_INDEX.json"
    if index.exists():
        try:
            data = json.loads(index.read_text(encoding="utf-8"))
            if data.get("schema") != "project-governor-context-index-v2":
                warnings.append(f"context index schema is {data.get('schema')}, expected v2")
        except Exception as exc:
            blockers.append(f"context index invalid JSON: {exc}")
    else:
        warnings.append("context index is missing; run context-indexer --write")
    docs_manifest = project / ".project-governor" / "context" / "DOCS_MANIFEST.json"
    if docs_manifest.exists():
        try:
            data = json.loads(docs_manifest.read_text(encoding="utf-8"))
            if data.get("schema") != "project-governor-docs-manifest-v1":
                warnings.append(f"docs manifest schema is {data.get('schema')}, expected project-governor-docs-manifest-v1")
        except Exception as exc:
            blockers.append(f"docs manifest invalid JSON: {exc}")
    else:
        warnings.append("docs manifest is missing; run context-indexer --write")
    state = project / ".project-governor" / "state"
    for rel in ["FEATURES.json", "AGENTS.json", "ISSUES.json", "PROGRESS.md", "SESSION.json"]:
        if not (state / rel).exists():
            warnings.append(f"state file missing: .project-governor/state/{rel}")
    for rel in [
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
    ]:
        compile_script(project / rel, blockers if execution_readiness else warnings)
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
