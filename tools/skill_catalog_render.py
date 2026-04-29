from __future__ import annotations

from typing import Any


def render_issue_lines(issues: list[dict[str, Any]]) -> list[str]:
    lines = ["issues:"]
    for item in issues:
        detail = item.get("skill") or item.get("category") or ""
        lines.append(f"- {item['severity']} {item['type']} {detail}: {item['message']}")
    return lines


def render_resolved_lines(items: list[dict[str, Any]]) -> list[str]:
    lines = ["resolved consolidations:"]
    if not items:
        return lines + ["- none"]
    for item in items[:20]:
        skills = ", ".join(item.get("skills", []))
        category = f" category={item['category']}" if "category" in item else ""
        resolved_by = f" resolved_by={item['resolved_by']}" if item.get("resolved_by") else ""
        lines.append(f"- {item['type']}{category}: {skills}{resolved_by}")
    return lines


def render_candidate_lines(items: list[dict[str, Any]]) -> list[str]:
    lines = ["consolidation candidates:"]
    if not items:
        return lines + ["- none"]
    for item in items[:20]:
        skills = ", ".join(item.get("skills", []))
        score = f" score={item['score']}" if "score" in item else ""
        category = f" category={item['category']}" if "category" in item else ""
        lines.append(f"- {item['type']}{category}{score}: {skills} -> {item['recommendation']}")
    return lines


def render_text(result: dict[str, Any]) -> str:
    lines = [
        f"status: {result['status']}",
        f"skills: {result['skill_count']}",
        f"catalog entries: {result['catalog_entry_count']}",
        "visibility counts:",
    ]
    for key, value in result["visibility_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.append("category counts:")
    for key, value in result["category_counts"].items():
        lines.append(f"- {key}: {value}")
    if result["issues"]:
        lines.extend(render_issue_lines(result["issues"]))
    lines.extend(render_resolved_lines(result["resolved_consolidations"]))
    lines.extend(render_candidate_lines(result["consolidation_candidates"]))
    return "\n".join(lines) + "\n"
