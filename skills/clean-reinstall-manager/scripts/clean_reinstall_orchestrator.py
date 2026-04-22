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
    reinstall = run_json([sys.executable, str(SCRIPT_DIR / "generate_reinstall_instructions.py")])

    if same_path(path, plugin_root):
        print(json.dumps({
            "status": "plugin_root_stop",
            "current_path": str(path),
            "plugin_root": str(plugin_root),
            "message": "Current directory is the Project Governor plugin root. No project files were modified.",
            "reinstall": reinstall,
            "next_commands": [
                "Run the refresh command from a governed target project.",
                "Or pass --discover-root to list governed projects before selecting refresh targets.",
            ],
        }, indent=2, ensure_ascii=False))
        return 0

    if is_project(path):
        refresh_cmd = [sys.executable, str(SCRIPT_DIR / "refresh_project_governance.py"), "--project", str(path), "--plugin-root", str(plugin_root)]
        if args.apply:
            refresh_cmd.append("--apply")
        if args.delete_trash:
            refresh_cmd.append("--delete-trash")
        refresh = run_json(refresh_cmd)
        print(json.dumps({"status": "project_refresh_ready", "current_path": str(path), "reinstall": reinstall, "refresh": refresh}, indent=2, ensure_ascii=False))
        return 0

    roots = args.discover_root or [Path.home()]
    discover_cmd = [sys.executable, str(SCRIPT_DIR / "discover_governed_projects.py")]
    for root in roots:
        discover_cmd.extend(["--root", str(root)])
    discovered = run_json(discover_cmd)
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
    if args.apply and args.select != "ignore":
        selected = discovered["projects"] if args.select == "all" else [p for p in discovered["projects"] if p["path"] in set(args.select.split(","))]
        applied = []
        for item in selected:
            refresh_cmd = [sys.executable, str(SCRIPT_DIR / "refresh_project_governance.py"), "--project", item["path"], "--plugin-root", str(plugin_root), "--apply"]
            if args.delete_trash:
                refresh_cmd.append("--delete-trash")
            applied.append(run_json(refresh_cmd))
        response["status"] = "selected_projects_refreshed"
        response["applied"] = applied
    print(json.dumps(response, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
