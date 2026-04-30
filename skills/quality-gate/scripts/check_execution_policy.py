#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_POLICY_REL = Path(".project-governor/runtime/EXECUTION_POLICY.json")
TEMPLATE_POLICY = ROOT / "templates" / ".project-governor" / "runtime" / "EXECUTION_POLICY.json"


def command_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("command", "cmd", "shell"):
            text = value.get(key)
            if isinstance(text, str):
                return text
    return ""


def normalize_commands(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value if (text := command_text(item))]
    if isinstance(value, dict):
        return normalize_commands(value.get("commands", []))
    return []


def execution_context(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    raw = data.get("execution_context", data.get("context", data.get("task_type", "")))
    if isinstance(raw, dict):
        context = raw.get("type", raw.get("context", raw.get("task_type", "")))
        return str(context), raw
    return str(raw), {}


def project_root(data: dict[str, Any], project: Path | None) -> Path:
    if project is not None:
        return project
    raw = data.get("project")
    if isinstance(raw, str) and raw:
        return Path(raw)
    return Path.cwd()


def resolve_policy_path(data: dict[str, Any], project: Path | None, policy: Path | None) -> Path | None:
    if policy is not None:
        return policy
    raw = data.get("execution_policy_path") or data.get("policy_path")
    if isinstance(raw, str) and raw:
        return Path(raw)
    candidate = project_root(data, project) / DEFAULT_POLICY_REL
    if candidate.exists():
        return candidate
    if TEMPLATE_POLICY.exists():
        return TEMPLATE_POLICY
    return None


def load_policy(data: dict[str, Any], project: Path | None = None, policy_path: Path | None = None) -> tuple[dict[str, Any] | None, str | None]:
    inline = data.get("execution_policy") or data.get("policy")
    if isinstance(inline, dict):
        return inline, "inline"
    if isinstance(inline, str) and inline:
        policy_path = Path(inline)
    resolved = resolve_policy_path(data, project, policy_path)
    if resolved is None or not resolved.exists():
        return None, str(resolved) if resolved is not None else None
    return json.loads(resolved.read_text(encoding="utf-8")), str(resolved)


def pattern_entry(value: Any) -> tuple[str, str]:
    if isinstance(value, str):
        return value, ""
    if isinstance(value, dict):
        pattern = value.get("pattern")
        if isinstance(pattern, str):
            message = value.get("message")
            return pattern, str(message) if message else ""
    return "", ""


def regex_matches(pattern: str, command: str) -> bool:
    return re.search(pattern, command) is not None


def override_approved(data: dict[str, Any], context_payload: dict[str, Any], policy_context: dict[str, Any]) -> bool:
    fields = [
        policy_context.get("override_field"),
        "execution_policy_override_approved",
        "override_approved",
        "allow_execution_policy_override",
    ]
    for field in fields:
        if isinstance(field, str) and field:
            if data.get(field) is True or context_payload.get(field) is True:
                return True
    return False


def invalid_pattern_finding(pattern: str, error: re.error) -> dict[str, Any]:
    return {
        "severity": "blocking",
        "type": "invalid_execution_policy_pattern",
        "pattern": pattern,
        "message": str(error),
    }


def disallowed_findings(
    *,
    commands: list[str],
    patterns: list[Any],
    overridden: bool,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for entry in patterns:
        pattern, message = pattern_entry(entry)
        if not pattern:
            continue
        try:
            matched = [command for command in commands if regex_matches(pattern, command)]
        except re.error as error:
            findings.append(invalid_pattern_finding(pattern, error))
            continue
        for command in matched:
            findings.append(
                {
                    "severity": "warning" if overridden else "blocking",
                    "type": "execution_command_disallowed" if not overridden else "execution_policy_override_used",
                    "pattern": pattern,
                    "command": command,
                    "message": message or "Command conflicts with the selected execution policy.",
                }
            )
    return findings


def required_any_findings(
    *,
    commands: list[str],
    patterns: list[Any],
    overridden: bool,
) -> list[dict[str, Any]]:
    if not patterns:
        return []
    pattern_texts: list[str] = []
    invalid: list[dict[str, Any]] = []
    for entry in patterns:
        pattern, _message = pattern_entry(entry)
        if not pattern:
            continue
        pattern_texts.append(pattern)
        try:
            if any(regex_matches(pattern, command) for command in commands):
                return []
        except re.error as error:
            invalid.append(invalid_pattern_finding(pattern, error))
    if invalid:
        return invalid
    if overridden:
        return [
            {
                "severity": "warning",
                "type": "execution_required_command_overridden",
                "required_any_patterns": pattern_texts,
                "message": "Required execution command pattern was bypassed by an explicit override.",
            }
        ]
    return [
        {
            "severity": "blocking",
            "type": "required_execution_command_missing",
            "required_any_patterns": pattern_texts,
            "message": "No recorded command matches the required execution policy patterns.",
        }
    ]


def result_payload(
    *,
    context: str,
    policy_source: str | None,
    commands: list[str],
    findings: list[dict[str, Any]],
    checked: bool,
    override: bool,
) -> dict[str, Any]:
    blockers = [item for item in findings if item.get("severity") == "blocking"]
    warnings = [item for item in findings if item.get("severity") != "blocking"]
    return {
        "status": "fail" if blockers else "pass",
        "schema": "project-governor-execution-policy-result-v1",
        "context": context,
        "checked": checked,
        "policy_source": policy_source,
        "override_approved": override,
        "commands_checked": commands,
        "findings": findings,
        "blockers": blockers,
        "warnings": warnings,
        "summary": {
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
            "commands_checked": len(commands),
        },
    }


def evaluate(data: dict[str, Any], *, project: Path | None = None, policy_path: Path | None = None) -> dict[str, Any]:
    context, context_payload = execution_context(data)
    commands = normalize_commands(context_payload.get("commands", data.get("commands", [])))
    policy, policy_source = load_policy(data, project=project, policy_path=policy_path)
    if not context:
        return result_payload(context="", policy_source=policy_source, commands=commands, findings=[], checked=False, override=False)
    if not isinstance(policy, dict):
        return result_payload(
            context=context,
            policy_source=policy_source,
            commands=commands,
            findings=[
                {
                    "severity": "warning",
                    "type": "execution_policy_missing",
                    "message": "Execution context was provided but no execution policy file was found.",
                }
            ],
            checked=False,
            override=False,
        )

    contexts = policy.get("contexts", {})
    policy_context = contexts.get(context) if isinstance(contexts, dict) else None
    if not isinstance(policy_context, dict):
        return result_payload(
            context=context,
            policy_source=policy_source,
            commands=commands,
            findings=[
                {
                    "severity": "warning",
                    "type": "execution_context_without_policy",
                    "message": f"No execution policy is defined for context: {context}",
                }
            ],
            checked=False,
            override=False,
        )

    overridden = override_approved(data, context_payload, policy_context)
    findings: list[dict[str, Any]] = []
    findings.extend(disallowed_findings(commands=commands, patterns=list(policy_context.get("disallowed_patterns", [])), overridden=overridden))
    findings.extend(required_any_findings(commands=commands, patterns=list(policy_context.get("required_any_patterns", [])), overridden=overridden))
    return result_payload(
        context=context,
        policy_source=policy_source,
        commands=commands,
        findings=findings,
        checked=True,
        override=overridden,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check recorded commands against Project Governor execution policy.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--project", type=Path, default=None)
    parser.add_argument("--policy", type=Path, default=None)
    args = parser.parse_args()
    result = evaluate(json.loads(args.input.read_text(encoding="utf-8")), project=args.project, policy_path=args.policy)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
