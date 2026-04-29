#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|private[_-]?key)\s*[:=]\s*['\"]?[^'\"\s]{6,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
]

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def today() -> str:
    return utc_now()[:10]

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


def contains_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def redact(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    return " ".join(redacted.split())


def short(text: str, limit: int = 180) -> str:
    text = redact(text)
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def cell(text: str) -> str:
    return short(text).replace("|", "\\|")


def stable_id(*parts: str) -> str:
    digest = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()
    return digest[:16]


def load_payload(path: Path | None) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8") if path else sys.stdin.read()
    if not raw.strip():
        raise SystemExit("Provide a JSON payload with learning items.")
    data = json.loads(raw)
    if isinstance(data, list):
        return {"items": data}
    if isinstance(data, dict):
        return data
    return {"items": [str(data)]}


def item_text(item: dict[str, Any]) -> str:
    fields = [
        item.get("text"),
        item.get("command"),
        item.get("error"),
        item.get("lesson"),
        item.get("reason"),
        item.get("memory"),
    ]
    return " ".join(str(value) for value in fields if value)


def normalize_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw_items = payload.get("items") or payload.get("events") or payload.get("learnings") or []
    items: list[dict[str, Any]] = []
    for raw in raw_items:
        if isinstance(raw, dict):
            items.append(dict(raw))
        else:
            items.append({"text": str(raw)})
    return items


def is_repeated(item: dict[str, Any], text: str) -> bool:
    repeat_count = item.get("repeat_count", 1)
    try:
        if int(repeat_count) >= 2:
            return True
    except Exception:
        pass
    lower = text.lower()
    return any(term in lower for term in ["repeated", "again", "keeps", "kept", "重复", "又", "再次"])


def has_signal(kind: str, lower: str, kinds: set[str], terms: list[str]) -> bool:
    return kind in kinds or any(term in lower for term in terms)


def secret_classification() -> dict[str, Any]:
    return {
        "classification": "secret_or_sensitive",
        "target_layer": "skip",
        "action": "do_not_store",
        "reason": "candidate contains secret-like content",
    }


def command_classification(item: dict[str, Any], text: str) -> dict[str, Any]:
    target = ".project-governor/state/COMMAND_LEARNINGS.json"
    if is_repeated(item, text):
        return {
            "classification": "repeated_mistake",
            "target_layer": "docs/memory/REPEATED_AGENT_MISTAKES.md",
            "action": "record_and_promote",
            "ledger": target,
        }
    return {
        "classification": "command_learning",
        "target_layer": target,
        "action": "record_for_next_session_memory_search",
    }


def layer_classification(classification: str, target_layer: str, action: str) -> dict[str, Any]:
    return {"classification": classification, "target_layer": target_layer, "action": action}


def repeated_signal(kind: str, lower: str) -> bool:
    return kind == "repeated_mistake" or "repeated mistake" in lower or "agent keeps" in lower or "codex keeps" in lower


def risk_signal(kind: str, lower: str) -> bool:
    return kind == "risk" or lower.startswith("risk:") or "risk register" in lower


def open_question_signal(kind: str, lower: str, text: str) -> bool:
    return kind == "open_question" or "?" in text or lower.startswith("question:") or "unknown" in lower or "unclear" in lower


def fallback_classifications(kind: str, lower: str, text: str) -> list[tuple[bool, dict[str, Any]]]:
    return [
        (
            has_signal(kind, lower, {"stale_memory", "stale_item", "superseded_memory"}, ["stale memory", "stale item", "superseded", "deprecated", "outdated", "过期", "失效"]),
            layer_classification("stale_memory", ".project-governor/state/MEMORY_HYGIENE.json", "queue_for_supersede_or_prune"),
        ),
        (repeated_signal(kind, lower), layer_classification("repeated_mistake", "docs/memory/REPEATED_AGENT_MISTAKES.md", "record_and_consider_rule")),
        (risk_signal(kind, lower), layer_classification("risk", "docs/memory/RISK_REGISTER.md", "record_risk")),
        (open_question_signal(kind, lower, text), layer_classification("open_question", "docs/memory/OPEN_QUESTIONS.md", "record_question")),
    ]


def classify(item: dict[str, Any]) -> dict[str, Any]:
    text = item_text(item)
    lower = text.lower()
    kind = str(item.get("type") or item.get("kind") or "").lower()
    if contains_secret(text):
        return secret_classification()

    command_signal = has_signal(kind, lower, {"command_failure", "failed_command", "command_error"}, ["command failed", "exit code", "returncode", "permission denied", "approval required", "命令失败", "执行错误"])
    if command_signal:
        return command_classification(item, text)
    for matched, result in fallback_classifications(kind, lower, text):
        if matched:
            return result
    return layer_classification("temporary_note", "task_or_session_only", "do_not_promote_without_evidence")


def ensure_markdown(path: Path, header: str, table_header: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "\n\n" + table_header + "\n", encoding="utf-8")


def append_line(path: Path, line: str, header: str, table_header: str) -> None:
    ensure_markdown(path, header, table_header)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def touch_existing_learning(entry: dict[str, Any]) -> None:
    entry["last_seen_at"] = utc_now()
    entry["times_seen"] = int(entry.get("times_seen", 1)) + 1
    entry["status"] = "active"


def touch_existing_hygiene(entry: dict[str, Any]) -> None:
    entry["last_seen_at"] = utc_now()
    entry["times_seen"] = int(entry.get("times_seen", 1)) + 1


def command_learning_fields(item: dict[str, Any], source: str) -> dict[str, str]:
    return {
        "command": short(str(item.get("command") or item.get("text") or "")),
        "error": short(str(item.get("error") or item.get("stderr") or "")),
        "lesson": short(str(item.get("lesson") or item.get("correct_behavior") or "Review this command before repeating it.")),
        "evidence": short(str(item.get("evidence") or source)),
    }


def repeat_count(item: dict[str, Any], repeated: bool) -> int:
    fallback = 2 if repeated else 1
    return int(item.get("repeat_count", fallback) or fallback)


def command_learning_entry(item: dict[str, Any], task_id: str, source: str, learning_id: str, repeated: bool) -> dict[str, Any]:
    fields = command_learning_fields(item, source)
    return {
        "id": learning_id,
        "date": today(),
        "task_id": task_id,
        "command": fields["command"],
        "error_signature": fields["error"],
        "lesson": fields["lesson"],
        "classification": "repeated_mistake" if repeated else "command_learning",
        "times_seen": repeat_count(item, repeated),
        "first_seen_at": utc_now(),
        "last_seen_at": utc_now(),
        "status": "active",
        "evidence": fields["evidence"],
    }


def upsert_learning(project: Path, item: dict[str, Any], task_id: str, source: str, repeated: bool = False) -> dict[str, Any]:
    path = project / ".project-governor" / "state" / "COMMAND_LEARNINGS.json"
    data = read_json(path, {"schema": "project-governor-command-learnings-v1", "learnings": []})
    command = short(str(item.get("command") or item.get("text") or ""))
    error = short(str(item.get("error") or item.get("stderr") or ""))
    lesson = short(str(item.get("lesson") or item.get("correct_behavior") or "Review this command before repeating it."))
    learning_id = stable_id(command, error, lesson)
    existing = next((entry for entry in data.setdefault("learnings", []) if entry.get("id") == learning_id), None)
    if existing:
        touch_existing_learning(existing)
        return {"path": str(path), "id": learning_id, "op": "updated"}
    data["learnings"].append(command_learning_entry(item, task_id, source, learning_id, repeated))
    write_json(path, data)
    return {"path": str(path), "id": learning_id, "op": "created"}


def hygiene_entry(item: dict[str, Any], task_id: str, source: str, hygiene_id: str) -> dict[str, Any]:
    return {
        "id": hygiene_id,
        "date": today(),
        "task_id": task_id,
        "subject": short(str(item.get("memory") or item.get("text") or item.get("path") or "stale memory candidate")),
        "source_path": str(item.get("path") or ""),
        "reason": short(str(item.get("reason") or item.get("evidence") or "Marked stale by session learning.")),
        "recommended_action": short(str(item.get("recommended_action") or "Mark superseded in source memory or prune during memory compaction.")),
        "status": "open",
        "times_seen": 1,
        "first_seen_at": utc_now(),
        "last_seen_at": utc_now(),
        "evidence": short(str(item.get("evidence") or source)),
    }


def record_hygiene(project: Path, item: dict[str, Any], task_id: str, source: str) -> dict[str, Any]:
    path = project / ".project-governor" / "state" / "MEMORY_HYGIENE.json"
    data = read_json(path, {"schema": "project-governor-memory-hygiene-v1", "items": []})
    subject = short(str(item.get("memory") or item.get("text") or item.get("path") or "stale memory candidate"))
    reason = short(str(item.get("reason") or item.get("evidence") or "Marked stale by session learning."))
    hygiene_id = stable_id(subject, reason)
    existing = next((entry for entry in data.setdefault("items", []) if entry.get("id") == hygiene_id), None)
    if existing:
        touch_existing_hygiene(existing)
        return {"path": str(path), "id": hygiene_id, "op": "updated"}
    data["items"].append(hygiene_entry(item, task_id, source, hygiene_id))
    write_json(path, data)
    return {"path": str(path), "id": hygiene_id, "op": "created"}


def append_repeated_mistake(project: Path, item: dict[str, Any], task_id: str, source: str) -> dict[str, Any]:
    learning = upsert_learning(project, item, task_id, source, repeated=True)
    mistake = cell(str(item.get("mistake") or item.get("text") or item.get("command") or "Repeated command/session mistake"))
    correct = cell(str(item.get("correct_behavior") or item.get("lesson") or "Check COMMAND_LEARNINGS before repeating this workflow."))
    evidence = cell(str(item.get("evidence") or source))
    path = project / "docs" / "memory" / "REPEATED_AGENT_MISTAKES.md"
    line = f"| {today()} | {mistake} | {correct} | {evidence} | `.project-governor/state/COMMAND_LEARNINGS.json` | active |"
    append_line(
        path,
        line,
        "# Repeated Agent Mistakes",
        "| Date | Mistake | Correct behavior | Evidence | Encoded where | Status |\n|---|---|---|---|---|---|",
    )
    return {"path": str(path), "id": learning["id"], "op": "appended"}


def append_open_question(project: Path, item: dict[str, Any], source: str) -> dict[str, Any]:
    question = cell(str(item.get("question") or item.get("text") or "Unresolved memory question"))
    why = cell(str(item.get("why") or item.get("reason") or "Needs human confirmation before promotion."))
    evidence = cell(str(item.get("evidence") or source))
    path = project / "docs" / "memory" / "OPEN_QUESTIONS.md"
    line = f"| {today()} | {question} | {why} | maintainer | open | {evidence} |"
    append_line(
        path,
        line,
        "# Open Questions",
        "| Date | Question | Why it matters | Owner | Status | Evidence |\n|---|---|---|---|---|---|",
    )
    return {"path": str(path), "op": "appended"}


def append_risk(project: Path, item: dict[str, Any], source: str) -> dict[str, Any]:
    risk = cell(str(item.get("risk") or item.get("text") or "Session learning risk"))
    impact = cell(str(item.get("impact") or "Future sessions may repeat an avoidable mistake."))
    mitigation = cell(str(item.get("mitigation") or item.get("lesson") or "Record learning and query memory-search at session start."))
    evidence = cell(str(item.get("evidence") or source))
    path = project / "docs" / "memory" / "RISK_REGISTER.md"
    line = f"| {today()} | {risk} | {impact} | medium | {mitigation} | maintainer | open | {evidence} |"
    append_line(
        path,
        line,
        "# Risk Register",
        "| Date | Risk | Impact | Likelihood | Mitigation | Owner | Status | Evidence |\n|---|---|---|---|---|---|---|---|",
    )
    return {"path": str(path), "op": "appended"}


def apply_item(project: Path, item: dict[str, Any], classified: dict[str, Any], task_id: str, source: str) -> list[dict[str, Any]]:
    kind = classified["classification"]
    if kind == "command_learning":
        return [upsert_learning(project, item, task_id, source)]
    if kind == "repeated_mistake":
        return [append_repeated_mistake(project, item, task_id, source)]
    if kind == "stale_memory":
        return [record_hygiene(project, item, task_id, source)]
    if kind == "open_question":
        return [append_open_question(project, item, source)]
    if kind == "risk":
        return [append_risk(project, item, source)]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Record session learnings into Project Governor memory layers.")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--input", type=Path)
    parser.add_argument("--task-id", default="session")
    parser.add_argument("--source", default="session_learning")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    project = args.project.resolve()
    payload = load_payload(args.input)
    task_id = str(payload.get("task_id") or args.task_id)
    source = str(payload.get("source") or args.source)
    results = []
    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for item in normalize_items(payload):
        classified = classify(item)
        result = {
            "text": short(item_text(item)),
            "classification": classified["classification"],
            "target_layer": classified["target_layer"],
            "action": classified["action"],
        }
        if args.apply and classified["classification"] != "secret_or_sensitive":
            writes = apply_item(project, item, classified, task_id, source)
            result["writes"] = writes
            applied.extend(writes)
        elif classified["classification"] == "secret_or_sensitive":
            skipped.append({"reason": "secret_or_sensitive", "target_layer": "skip"})
        results.append(result)

    output = {
        "status": "applied" if args.apply else "planned",
        "schema": "project-governor-session-learning-v1",
        "project": str(project),
        "task_id": task_id,
        "results": results,
        "applied": applied,
        "skipped": skipped,
        "memory_search_followup": (
            "python3 skills/context-indexer/scripts/query_context_index.py --project . "
            f"--request {json.dumps(task_id + ' command learning memory hygiene')} --memory-search --auto-build --format text"
        ),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
