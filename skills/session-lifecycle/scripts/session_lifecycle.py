#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def state_dir(project: Path) -> Path:
    return project / ".project-governor" / "state"


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def git_status(project: Path) -> dict[str, Any]:
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=project, text=True, capture_output=True, timeout=5, check=False).stdout.strip()
        status = subprocess.run(["git", "status", "--porcelain"], cwd=project, text=True, capture_output=True, timeout=5, check=False).stdout
    except Exception:
        return {"head": None, "dirty": None, "changed_files": []}
    changed = []
    for line in status.splitlines():
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
    return {"head": head or None, "dirty": bool(status.strip()), "changed_files": changed}


def ensure_state(project: Path) -> None:
    sd = state_dir(project)
    sd.mkdir(parents=True, exist_ok=True)
    defaults = {
        "FEATURES.json": {"schema": "project-governor-features-v1", "features": []},
        "AGENTS.json": {"schema": "project-governor-agents-v1", "agents": []},
        "ISSUES.json": {"schema": "project-governor-issues-v1", "issues": []},
        "COMMAND_LEARNINGS.json": {"schema": "project-governor-command-learnings-v1", "learnings": []},
        "MEMORY_HYGIENE.json": {"schema": "project-governor-memory-hygiene-v1", "items": []},
        "QUALITY_SCORE.json": {"schema": "project-governor-quality-score-v1", "score": None, "last_updated": None},
    }
    for name, data in defaults.items():
        path = sd / name
        if not path.exists():
            write_json(path, data)
    progress = sd / "PROGRESS.md"
    if not progress.exists():
        progress.write_text("# Project Governor Progress\n\n", encoding="utf-8")


def start(project: Path, task_id: str, route: str, target_files: list[str]) -> dict[str, Any]:
    ensure_state(project)
    session_id = f"{utc_now().replace(':', '').replace('-', '').replace('Z', 'Z')}-{task_id}"
    session = {
        "schema": "project-governor-session-v1",
        "session_id": session_id,
        "task_id": task_id,
        "route": route,
        "status": "active",
        "started_at": utc_now(),
        "ended_at": None,
        "target_files": target_files,
        "git": git_status(project),
        "evidence_path": str(project / ".project-governor" / "evidence" / task_id / "EVIDENCE.json"),
    }
    write_json(state_dir(project) / "SESSION.json", session)
    progress = state_dir(project) / "PROGRESS.md"
    with progress.open("a", encoding="utf-8") as fh:
        fh.write(f"## {session['started_at']} session-start {task_id}\n\n- route: `{route}`\n- target_files: {target_files}\n\n")
    return {"status": "started", "session": session}


def end(project: Path, status: str, summary: str, evidence_path: str | None, commands: list[str]) -> dict[str, Any]:
    ensure_state(project)
    path = state_dir(project) / "SESSION.json"
    session = read_json(path, {"schema": "project-governor-session-v1"})
    session["status"] = status
    session["ended_at"] = utc_now()
    if evidence_path:
        session["evidence_path"] = evidence_path
    session["commands"] = commands
    write_json(path, session)
    progress = state_dir(project) / "PROGRESS.md"
    with progress.open("a", encoding="utf-8") as fh:
        fh.write(f"## {session['ended_at']} session-end {session.get('task_id', 'task')}\n\n- status: `{status}`\n- evidence: `{session.get('evidence_path')}`\n- commands: {commands}\n- summary: {summary}\n\n")
    return {"status": "ended", "session": session}


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Governor Harness v6 session lifecycle manager.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--project", type=Path, default=Path.cwd())
    s.add_argument("--task-id", default="task")
    s.add_argument("--route", default="standard_feature")
    s.add_argument("--target-file", action="append", default=[])
    e = sub.add_parser("end")
    e.add_argument("--project", type=Path, default=Path.cwd())
    e.add_argument("--status", default="completed")
    e.add_argument("--summary", default="")
    e.add_argument("--evidence-path")
    e.add_argument("--command", action="append", default=[])
    args = parser.parse_args()
    project = args.project.resolve()
    if args.cmd == "start":
        result = start(project, args.task_id, args.route, args.target_file)
    else:
        result = end(project, args.status, args.summary, args.evidence_path, args.command)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
