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


def fallback_runtime_payload() -> dict:
    return {
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


def runtime_template_payloads(plugin_root: Path) -> list[tuple[str, Path | None, dict]]:
    runtime_dir = plugin_root / "templates" / ".project-governor" / "runtime"
    payloads: list[tuple[str, Path | None, dict]] = []
    if runtime_dir.exists():
        for source in sorted(runtime_dir.glob("*.json")):
            payloads.append((source.name, source, json.loads(source.read_text(encoding="utf-8"))))
    if not any(name == "GPT55_RUNTIME_MODE.json" for name, _source, _payload in payloads):
        payloads.append(("GPT55_RUNTIME_MODE.json", None, fallback_runtime_payload()))
    return payloads


def write_runtime(project: Path, plugin_root: Path, *, apply: bool) -> dict:
    runtime_files = []
    for filename, source, payload in runtime_template_payloads(plugin_root):
        target = project / ".project-governor" / "runtime" / filename
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        runtime_files.append(
            {
                "status": "written" if apply else "planned",
                "path": str(target),
                "source": str(source) if source else "fallback",
                "payload": payload,
            }
        )

    primary = next((item for item in runtime_files if item["path"].endswith("GPT55_RUNTIME_MODE.json")), runtime_files[0])
    return {
        "status": "written" if apply else "planned",
        "path": primary["path"],
        "payload": primary["payload"],
        "files": runtime_files,
    }


def apply_project(project: Path, plugin_root: Path, *, apply: bool) -> dict:
    runtime = write_runtime(project, plugin_root, apply=apply)
    index = build_index(project, plugin_root) if apply else {"status": "planned", "reason": "run with --apply to build context index"}
    return {"project": str(project), "runtime": runtime, "context_index": index}


def discover_projects(roots: list[Path]) -> list[dict]:
    discovered: list[dict] = []
    for root in roots:
        if root.exists():
            discovered.extend(discover(root.resolve()))
    return discovered


def not_project_response(discovered: list[dict]) -> dict:
    return {
        "status": "not_project_stop",
        "message": "Current directory is not a Project Governor project. No project files were modified.",
        "discovered_projects": discovered,
        "user_choices": ["ignore", "all", "selected"],
    }


def select_projects(discovered: list[dict], select: str) -> list[dict]:
    if select == "all":
        return discovered
    selected_paths = set(select.split(","))
    return [project for project in discovered if project["path"] in selected_paths]


def selected_runtime_response(selected: list[dict], plugin_root: Path, apply: bool) -> dict:
    results = [apply_project(Path(item["path"]), plugin_root, apply=apply) for item in selected]
    return {"status": "selected_projects_runtime_mode_ready", "selected_count": len(selected), "results": results}


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
    discovered = discover_projects(roots)
    if not is_project(path) and args.select in {"current", "ignore"}:
        print(json.dumps(not_project_response(discovered), indent=2, ensure_ascii=False))
        return 0

    selected = select_projects(discovered, args.select)
    print(json.dumps(selected_runtime_response(selected, plugin_root, args.apply), indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
