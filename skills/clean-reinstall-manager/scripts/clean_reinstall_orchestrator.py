#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def run_json(command: list[str]) -> dict:
    proc = subprocess.run(command, text=True, capture_output=True, check=True)
    return json.loads(proc.stdout)


def is_project(path: Path) -> bool:
    return any([
        (path / ".project-governor" / "INSTALL_MANIFEST.json").exists(),
        (path / "AGENTS.md").exists() and "Project Governor" in path.joinpath("AGENTS.md").read_text(encoding="utf-8", errors="ignore"),
        (path / "docs" / "conventions" / "ITERATION_CONTRACT.md").exists(),
    ])


def same_path(left: Path, right: Path) -> bool:
    return left.resolve() == right.resolve()


def reinstall_instructions() -> dict:
    return run_json([sys.executable, str(SCRIPT_DIR / "generate_reinstall_instructions.py")])


def refresh_command(path: Path | str, plugin_root: Path, apply: bool, delete_trash: bool) -> list[str]:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "refresh_project_governance.py"),
        "--project",
        str(path),
        "--plugin-root",
        str(plugin_root),
    ]
    if apply:
        command.append("--apply")
    if delete_trash:
        command.append("--delete-trash")
    return command


def plugin_root_response(path: Path, plugin_root: Path, reinstall: dict) -> dict:
    return {
        "status": "plugin_root_stop",
        "current_path": str(path),
        "plugin_root": str(plugin_root),
        "message": "Current directory is the Project Governor plugin root. No project files were modified.",
        "reinstall": reinstall,
        "next_commands": [
            "Run the refresh command from a governed target project.",
            "Or pass --discover-root to list governed projects before selecting refresh targets.",
        ],
    }


def project_refresh_response(path: Path, plugin_root: Path, reinstall: dict, apply: bool, delete_trash: bool) -> dict:
    refresh = run_json(refresh_command(path, plugin_root, apply, delete_trash))
    return {
        "status": "project_refresh_ready",
        "current_path": str(path),
        "reinstall": reinstall,
        "refresh": refresh,
    }


def discover_projects(roots: list[Path]) -> dict:
    discover_cmd = [sys.executable, str(SCRIPT_DIR / "discover_governed_projects.py")]
    for root in roots:
        discover_cmd.extend(["--root", str(root)])
    return run_json(discover_cmd)


def select_projects(projects: list[dict], select: str) -> list[dict]:
    if select == "all":
        return projects
    selected_paths = set(select.split(","))
    return [project for project in projects if project["path"] in selected_paths]


def applied_refreshes(projects: list[dict], plugin_root: Path, delete_trash: bool) -> list[dict]:
    return [
        run_json(refresh_command(project["path"], plugin_root, apply=True, delete_trash=delete_trash))
        for project in projects
    ]


def discovery_response(path: Path, roots: list[Path], plugin_root: Path, reinstall: dict, apply: bool, select: str, delete_trash: bool) -> dict:
    discovered = discover_projects(roots)
    response = {
        "status": "not_project_stop",
        "current_path": str(path),
        "message": "Current directory is not a Project Governor project. No project files were modified.",
        "reinstall": reinstall,
        "discovered_projects": discovered["projects"],
        "user_choices": ["ignore", "all", "selected"],
        "next_commands": [
            "Run again inside a discovered project.",
            "Or run with --select all --apply to refresh all discovered projects.",
            "Or run with --select /path/one,/path/two --apply for selected projects.",
        ],
    }
    if apply and select != "ignore":
        response["status"] = "selected_projects_refreshed"
        response["applied"] = applied_refreshes(select_projects(discovered["projects"], select), plugin_root, delete_trash)
    return response


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=Path.cwd())
    parser.add_argument("--plugin-root", type=Path, required=True)
    parser.add_argument("--discover-root", action="append", type=Path, default=[])
    parser.add_argument("--select", default="ignore", help="ignore, all, or comma-separated project paths")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--delete-trash", action="store_true")
    args = parser.parse_args()

    path = args.path.resolve()
    plugin_root = args.plugin_root.resolve()
    reinstall = reinstall_instructions()

    if same_path(path, plugin_root):
        response = plugin_root_response(path, plugin_root, reinstall)
    elif is_project(path):
        response = project_refresh_response(path, plugin_root, reinstall, args.apply, args.delete_trash)
    else:
        response = discovery_response(path, args.discover_root or [Path.home()], plugin_root, reinstall, args.apply, args.select, args.delete_trash)
    print(json.dumps(response, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
