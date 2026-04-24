#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def is_project(path: Path) -> bool:
    return any([
        (path / ".project-governor" / "INSTALL_MANIFEST.json").exists(),
        (path / "AGENTS.md").exists() and "Project Governor" in (path / "AGENTS.md").read_text(encoding="utf-8", errors="ignore"),
        (path / "docs" / "conventions" / "ITERATION_CONTRACT.md").exists(),
    ])


def discover(root: Path) -> list[dict]:
    projects = []
    for p in root.rglob(".project-governor"):
        if p.is_dir():
            project = p.parent
            if is_project(project):
                projects.append({"path": str(project.resolve())})
    return projects


def build_index(project: Path, plugin_root: Path) -> dict:
    script = plugin_root / "skills" / "context-indexer" / "scripts" / "build_context_index.py"
    if not script.exists():
        return {"status": "skipped", "reason": "context-indexer not installed"}
    proc = subprocess.run([sys.executable, str(script), "--project", str(project), "--write"], text=True, capture_output=True, check=True)
    return json.loads(proc.stdout)


def write_runtime(project: Path, *, apply: bool) -> dict:
    target = project / ".project-governor" / "runtime" / "GPT55_RUNTIME_MODE.json"
    payload = {
        "schema": "project-governor-runtime-mode-v1",
        "mode": "gpt55-auto-orchestration",
        "model_policy": {
            "primary": "gpt-5.5",
            "fallback_primary": "gpt-5.4",
            "fast_scout": "gpt-5.4-mini",
            "high_reasoning": "gpt-5.5",
            "micro_patch_can_use_fast_scout": True,
        },
        "context_policy": {
            "read_all_initialization_docs_on_session_start": False,
            "prefer_session_brief": ".project-governor/context/SESSION_BRIEF.md",
            "prefer_context_index": ".project-governor/context/CONTEXT_INDEX.json",
        },
        "automation_policy": {
            "auto_select_skills": True,
            "auto_select_subagents": True,
            "micro_patch_skips_subagents": True,
            "strict_routes_require_subagents": True,
        },
        "hygiene_policy": {
            "do_not_copy_plugin_global_assets": True,
            "project_runtime_state_only": True,
        },
    }
    if apply:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"status": "written" if apply else "planned", "path": str(target), "payload": payload}


def apply_project(project: Path, plugin_root: Path, *, apply: bool) -> dict:
    runtime = write_runtime(project, apply=apply)
    index = build_index(project, plugin_root) if apply else {"status": "planned", "reason": "run with --apply to build context index"}
    return {"project": str(project), "runtime": runtime, "context_index": index}


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply GPT-5.5 Project Governor runtime mode to one or more governed projects.")
    parser.add_argument("--path", type=Path, default=Path.cwd())
    parser.add_argument("--plugin-root", type=Path, required=True)
    parser.add_argument("--discover-root", action="append", type=Path, default=[])
    parser.add_argument("--select", default="current", help="current, all, ignore, or comma-separated project paths")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    path = args.path.resolve()
    plugin_root = args.plugin_root.resolve()
    if is_project(path) and args.select in {"current", "all"}:
        result = apply_project(path, plugin_root, apply=args.apply)
        print(json.dumps({"status": "project_runtime_mode_ready", "result": result}, indent=2, ensure_ascii=False))
        return 0

    roots = args.discover_root or [Path.home()]
    discovered = []
    for root in roots:
        if root.exists():
            discovered.extend(discover(root.resolve()))
    if not is_project(path) and args.select in {"current", "ignore"}:
        print(json.dumps({
            "status": "not_project_stop",
            "message": "Current directory is not a Project Governor project. No project files were modified.",
            "discovered_projects": discovered,
            "user_choices": ["ignore", "all", "selected"],
        }, indent=2, ensure_ascii=False))
        return 0

    selected = discovered if args.select == "all" else [p for p in discovered if p["path"] in set(args.select.split(","))]
    results = [apply_project(Path(item["path"]), plugin_root, apply=args.apply) for item in selected]
    print(json.dumps({"status": "selected_projects_runtime_mode_ready", "selected_count": len(selected), "results": results}, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
