#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from standards_core import (
    ASSERTION_RE,
    MOCK_DATA_RE,
    MOCK_IMPORT_RE,
    Thresholds,
    add_finding,
    complexity,
    diff_added_files,
    diff_changed_lines,
    diff_paths,
    filter_diff_findings,
    function_spans,
    import_values,
    is_test_like,
    iter_source_files,
    relpath,
    strip_string_literals,
    untracked_paths,
)


def check_file_size(relative: str, line_count: int, thresholds: Thresholds) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if line_count > thresholds.file_fail_lines:
        add_finding(
            findings,
            severity="blocking",
            type_="source_file_too_large",
            path=relative,
            message=f"Source file has {line_count} lines, above blocking threshold {thresholds.file_fail_lines}.",
            rule="file_size",
            recommendation="Split by responsibility or reuse existing modules before adding more code.",
            line_count=line_count,
            threshold=thresholds.file_fail_lines,
        )
    elif line_count > thresholds.file_warn_lines:
        add_finding(
            findings,
            severity="warning",
            type_="source_file_large",
            path=relative,
            message=f"Source file has {line_count} lines, above warning threshold {thresholds.file_warn_lines}.",
            rule="file_size",
            recommendation="Avoid growing this file further without an extraction plan.",
            line_count=line_count,
            threshold=thresholds.file_warn_lines,
        )
    return findings


def add_function_size_finding(
    findings: list[dict[str, Any]],
    *,
    relative: str,
    name: str,
    start: int,
    end: int,
    function_lines: int,
    thresholds: Thresholds,
) -> None:
    if function_lines > thresholds.function_fail_lines:
        add_finding(
            findings,
            severity="blocking",
            type_="function_too_long",
            path=relative,
            line=start,
            message=f"Function `{name}` spans {function_lines} lines, above blocking threshold {thresholds.function_fail_lines}.",
            rule="function_size",
            recommendation="Extract cohesive helpers or split responsibilities while preserving existing contracts.",
            symbol=name,
            line_count=function_lines,
            line_end=end,
            threshold=thresholds.function_fail_lines,
        )
    elif function_lines > thresholds.function_warn_lines:
        add_finding(
            findings,
            severity="warning",
            type_="function_large",
            path=relative,
            line=start,
            message=f"Function `{name}` spans {function_lines} lines, above warning threshold {thresholds.function_warn_lines}.",
            rule="function_size",
            recommendation="Consider extraction if this function grows further.",
            symbol=name,
            line_count=function_lines,
            line_end=end,
            threshold=thresholds.function_warn_lines,
        )


def add_complexity_finding(
    findings: list[dict[str, Any]],
    *,
    relative: str,
    name: str,
    start: int,
    end: int,
    score: int,
    thresholds: Thresholds,
) -> None:
    if score > thresholds.complexity_fail:
        add_finding(
            findings,
            severity="blocking",
            type_="function_too_complex",
            path=relative,
            line=start,
            message=f"Function `{name}` has approximate complexity {score}, above blocking threshold {thresholds.complexity_fail}.",
            rule="complexity",
            recommendation="Split decision branches or table-drive the logic with focused tests.",
            symbol=name,
            complexity=score,
            line_end=end,
            threshold=thresholds.complexity_fail,
        )
    elif score > thresholds.complexity_warn:
        add_finding(
            findings,
            severity="warning",
            type_="function_complex",
            path=relative,
            line=start,
            message=f"Function `{name}` has approximate complexity {score}, above warning threshold {thresholds.complexity_warn}.",
            rule="complexity",
            recommendation="Add focused tests and avoid adding more branches.",
            symbol=name,
            complexity=score,
            line_end=end,
            threshold=thresholds.complexity_warn,
        )


def check_functions(path: Path, relative: str, lines: list[str], thresholds: Thresholds) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for name, start, end in function_spans(path, lines):
        block = "\n".join(lines[start - 1:end])
        function_lines = max(1, end - start + 1)
        add_function_size_finding(
            findings,
            relative=relative,
            name=name,
            start=start,
            end=end,
            function_lines=function_lines,
            thresholds=thresholds,
        )
        add_complexity_finding(
            findings,
            relative=relative,
            name=name,
            start=start,
            end=end,
            score=complexity(block),
            thresholds=thresholds,
        )
    return findings


def collect_mock_imports(relative: str, text: str, test_like: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    mock_inventory: list[dict[str, Any]] = []
    for line, value in import_values(text):
        if not MOCK_IMPORT_RE.search(value):
            continue
        scope = "test_support" if test_like else "production"
        mock_inventory.append({"path": relative, "line": line, "signal": "mock_import", "value": value, "scope": scope})
        if not test_like:
            add_finding(
                findings,
                severity="blocking",
                type_="production_mock_import",
                path=relative,
                line=line,
                message=f"Production file imports mock/test-only dependency `{value}`.",
                rule="mock_leakage",
                recommendation="Move the mock to tests/fixtures or replace it with the real service/client path.",
                import_path=value,
            )
    return findings, mock_inventory


def is_regex_definition_line(line_text: str) -> bool:
    return "re.compile(" in line_text or line_text.strip().endswith("_RE = re.compile(")


def collect_mock_identifiers(relative: str, text: str, lines: list[str], test_like: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    mock_inventory: list[dict[str, Any]] = []
    if test_like:
        return findings, mock_inventory
    searchable = strip_string_literals(text)
    for match in MOCK_DATA_RE.finditer(searchable):
        line = searchable.count("\n", 0, match.start()) + 1
        if 1 <= line <= len(lines) and is_regex_definition_line(lines[line - 1]):
            continue
        value = match.group(0)
        mock_inventory.append({"path": relative, "line": line, "signal": "mock_like_identifier", "value": value, "scope": "production"})
        add_finding(
            findings,
            severity="warning",
            type_="mock_like_production_data",
            path=relative,
            line=line,
            message=f"Production file contains mock-like identifier `{value}`.",
            rule="mock_leakage",
            recommendation="Confirm this is not leftover mock/demo data; move test data to fixtures when possible.",
            identifier=value,
        )
    return findings, mock_inventory


def check_test_assertions(relative: str, text: str, test_like: bool) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if test_like and re.search(r"\b(test|it|describe)\s*\(", text) and not ASSERTION_RE.search(text):
        add_finding(
            findings,
            severity="warning",
            type_="test_without_assertions",
            path=relative,
            message="Test file defines test cases but no assertion marker was found.",
            rule="test_hygiene",
            recommendation="Add assertions that verify behavior, errors, boundaries, or integration contracts.",
        )
    return findings


def scan_file(path: Path, project: Path, thresholds: Thresholds) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    relative = relpath(path, project)
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    line_count = len(lines)
    test_like = is_test_like(path, project)
    findings = check_file_size(relative, line_count, thresholds)
    findings.extend(check_functions(path, relative, lines, thresholds))
    import_findings, import_mocks = collect_mock_imports(relative, text, test_like)
    identifier_findings, identifier_mocks = collect_mock_identifiers(relative, text, lines, test_like)
    findings.extend(import_findings)
    findings.extend(identifier_findings)
    findings.extend(check_test_assertions(relative, text, test_like))

    metrics = {
        "path": relative,
        "line_count": line_count,
        "is_test_like": test_like,
        "function_count": len(function_spans(path, lines)),
    }
    return metrics, findings, import_mocks + identifier_mocks


def resolve_scope(project: Path, scope: str, diff_base: str | None) -> tuple[list[str] | None, dict[str, set[int]], set[str], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    if scope != "diff":
        return None, {}, set(), findings
    if not diff_base:
        add_finding(
            findings,
            severity="warning",
            type_="diff_scope_unavailable",
            path=".",
            message="Diff scope requested without --diff-base; scanned no files.",
            rule="scope",
            recommendation="Run with --scope all or provide a valid git diff base.",
        )
        return [], {}, set(), findings

    scoped_paths, diff_error = diff_paths(project, diff_base)
    untracked = untracked_paths(project)
    if diff_error:
        add_finding(
            findings,
            severity="warning",
            type_="diff_scope_unavailable",
            path=".",
            message=diff_error,
            rule="scope",
            recommendation="Run with --scope all or provide a valid git diff base.",
        )
        return untracked, {}, set(untracked), findings
    return scoped_paths + untracked, diff_changed_lines(project, diff_base), diff_added_files(project, diff_base) | set(untracked), findings


def scan_project(
    project: Path,
    paths: list[str] | None,
    thresholds: Thresholds,
    *,
    scope: str,
    changed_lines_by_file: dict[str, set[int]],
    added_files: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int]:
    files: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    mock_inventory: list[dict[str, Any]] = []
    suppressed_baseline_count = 0

    for path in iter_source_files(project, paths):
        metrics, file_findings, file_mocks = scan_file(path, project, thresholds)
        if scope == "diff":
            file_findings, suppressed = filter_diff_findings(
                file_findings,
                changed_lines=changed_lines_by_file.get(metrics["path"], set()),
                added_file=metrics["path"] in added_files,
            )
            suppressed_baseline_count += suppressed
        files.append(metrics)
        findings.extend(file_findings)
        mock_inventory.extend(file_mocks)
    return files, findings, mock_inventory, suppressed_baseline_count


def check(project: Path, *, scope: str = "all", diff_base: str | None = None, thresholds: Thresholds | None = None) -> dict[str, Any]:
    project = project.resolve()
    thresholds = thresholds or Thresholds()
    scoped_paths, changed_lines_by_file, added_files, scope_findings = resolve_scope(project, scope, diff_base)
    files, findings, mock_inventory, suppressed_baseline_count = scan_project(
        project,
        scoped_paths,
        thresholds,
        scope=scope,
        changed_lines_by_file=changed_lines_by_file,
        added_files=added_files,
    )
    findings = scope_findings + findings

    blockers = [item for item in findings if item["severity"] == "blocking"]
    warnings = [item for item in findings if item["severity"] != "blocking"]
    status = "fail" if blockers else ("warn" if warnings else "pass")
    return {
        "schema": "project-governor-engineering-standards-v1",
        "status": status,
        "project": str(project),
        "scope": scope,
        "diff_base": diff_base,
        "thresholds": {
            "file_warn_lines": thresholds.file_warn_lines,
            "file_fail_lines": thresholds.file_fail_lines,
            "function_warn_lines": thresholds.function_warn_lines,
            "function_fail_lines": thresholds.function_fail_lines,
            "complexity_warn": thresholds.complexity_warn,
            "complexity_fail": thresholds.complexity_fail,
        },
        "summary": {
            "files_scanned": len(files),
            "blocker_count": len(blockers),
            "warning_count": len(warnings),
            "mock_inventory_count": len(mock_inventory),
            "test_like_files": sum(1 for item in files if item["is_test_like"]),
            "suppressed_baseline_count": suppressed_baseline_count,
        },
        "files": files,
        "mock_inventory": mock_inventory,
        "findings": findings,
        "blockers": blockers,
        "warnings": warnings,
    }


def format_text(result: dict[str, Any]) -> str:
    lines = [
        f"Engineering standards: {result['status']}",
        f"Files scanned: {result['summary']['files_scanned']}",
        f"Blockers: {result['summary']['blocker_count']}",
        f"Warnings: {result['summary']['warning_count']}",
    ]
    for finding in result["findings"]:
        location = finding["path"]
        if "line" in finding:
            location = f"{location}:{finding['line']}"
        lines.append(f"- {finding['severity']} {finding['type']} {location}: {finding['message']}")
    return "\n".join(lines)


