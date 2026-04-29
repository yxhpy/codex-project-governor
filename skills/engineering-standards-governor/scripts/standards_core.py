#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SOURCE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}
IGNORED_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".next",
    ".project-governor/context",
    ".pytest_cache",
    ".tox",
    ".turbo",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
    "venv",
}
TEST_PARTS = {
    "__mocks__",
    "__tests__",
    "fixture",
    "fixtures",
    "mock",
    "mocks",
    "spec",
    "test",
    "testdata",
    "tests",
}
TEST_SUFFIX_RE = re.compile(r"(\.|_)(test|spec|mock|fixture)\.[^.]+$", re.IGNORECASE)
ASSERTION_RE = re.compile(
    r"\b(expect|assert|assertThat|assertEquals|assertTrue|assertFalse|verify|should|toBe|toEqual|toContain|pytest\.raises|raises|screen\.|cy\.|page\.)\b|"
    r"\bself\.assert|assert\s+",
    re.IGNORECASE,
)
IMPORT_RE = re.compile(
    r"(?:from\s+['\"]([^'\"]+)['\"]|import\s+[^;\n]*?\s+from\s+['\"]([^'\"]+)['\"]|require\(\s*['\"]([^'\"]+)['\"]\s*\)|"
    r"^\s*from\s+([A-Za-z0-9_.$]+)\s+import\b|^\s*import\s+([A-Za-z0-9_.$]+))",
    re.MULTILINE,
)
MOCK_IMPORT_RE = re.compile(
    r"(^|[/._-])(__mocks__|mocks?|fixtures?|testdata|tests?)([/._-]|$)|(^|[/._-])(mock|fixture)([/._-])|"
    r"^(@faker-js/faker|faker|msw|msw/node|sinon)$",
    re.IGNORECASE,
)
MOCK_DATA_RE = re.compile(
    r"\b(mockData|mockResponse|mockUser|fakeUser|fakeData|demoData|sampleResponse|stubResponse|TODO:?\s+mock)\b",
    re.IGNORECASE,
)
STRING_LITERAL_RE = re.compile(r"'''[\s\S]*?'''|\"\"\"[\s\S]*?\"\"\"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"")
PY_FUNCTION_RE = re.compile(r"^(?P<indent>\s*)(?:async\s+def|def)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\(")
JS_FUNCTION_RE = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?function\s+(?P<name>[A-Za-z_$][A-Za-z0-9_$]*)\s*\(|"
    r"^\s*(?:export\s+)?(?:const|let|var)\s+(?P<arrow>[A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][A-Za-z0-9_$]*)\s*=>|"
    r"^\s*(?:public\s+|private\s+|protected\s+|static\s+|async\s+|final\s+|override\s+)*(?P<method>[A-Za-z_$][A-Za-z0-9_$]*)\s*\([^;{}]*\)\s*\{"
)
CONTROL_FLOW_RE = re.compile(
    r"\b(if|elif|else\s+if|for|while|case|catch|except|when|guard)\b|&&|\|\||\?|"
    r"\b(and|or)\b",
    re.IGNORECASE,
)
CONTROL_NAMES = {"if", "for", "while", "switch", "catch", "return", "function"}


@dataclass(frozen=True)
class Thresholds:
    file_warn_lines: int = 400
    file_fail_lines: int = 800
    function_warn_lines: int = 60
    function_fail_lines: int = 100
    complexity_warn: int = 10
    complexity_fail: int = 15


def relpath(path: Path, project: Path) -> str:
    try:
        return path.relative_to(project).as_posix()
    except ValueError:
        return path.as_posix()


def has_ignored_part(path: Path, project: Path) -> bool:
    relative = relpath(path, project)
    parts = relative.split("/")
    for ignored in IGNORED_DIRS:
        ignored_parts = ignored.split("/")
        for index in range(0, len(parts) - len(ignored_parts) + 1):
            if parts[index:index + len(ignored_parts)] == ignored_parts:
                return True
    return False


def is_source_file(path: Path) -> bool:
    if path.suffix not in SOURCE_EXTENSIONS:
        return False
    if path.name.endswith(".min.js") or path.name.endswith(".bundle.js"):
        return False
    return True


def is_test_like(path: Path, project: Path) -> bool:
    relative = relpath(path, project)
    lower_parts = {part.lower() for part in Path(relative).parts}
    if lower_parts & TEST_PARTS:
        return True
    return bool(TEST_SUFFIX_RE.search(path.name))


def iter_source_files(project: Path, scoped_paths: Iterable[str] | None = None) -> list[Path]:
    if scoped_paths is not None:
        candidates = [project / item for item in scoped_paths]
    else:
        candidates = list(project.rglob("*"))
    return sorted(
        path
        for path in candidates
        if path.is_file() and is_source_file(path) and not has_ignored_part(path, project)
    )


def diff_paths(project: Path, base: str) -> tuple[list[str], str | None]:
    try:
        process = subprocess.run(
            ["git", "-C", str(project), "diff", "--name-only", base, "--"],
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return [], f"Could not collect git diff paths from {base}: {exc}"
    return [line.strip() for line in process.stdout.splitlines() if line.strip()], None


def diff_added_files(project: Path, base: str) -> set[str]:
    try:
        process = subprocess.run(
            ["git", "-C", str(project), "diff", "--name-status", base, "--"],
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return set()
    added: set[str] = set()
    for line in process.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0] == "A":
            added.add(parts[1])
    return added


def untracked_paths(project: Path) -> list[str]:
    try:
        process = subprocess.run(
            ["git", "-C", str(project), "ls-files", "--others", "--exclude-standard"],
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []
    return [line.strip() for line in process.stdout.splitlines() if line.strip()]


def git_diff_unified(project: Path, base: str) -> list[str]:
    try:
        process = subprocess.run(
            ["git", "-C", str(project), "diff", "--unified=0", "--no-color", base, "--"],
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []
    return process.stdout.splitlines()


def hunk_start(line: str) -> int | None:
    match = re.search(r"\+(\d+)(?:,(\d+))?", line)
    return int(match.group(1)) if match else None


def diff_changed_lines(project: Path, base: str) -> dict[str, set[int]]:
    changed: dict[str, set[int]] = {}
    current_path: str | None = None
    next_new_line: int | None = None
    for line in git_diff_unified(project, base):
        if line.startswith("+++ b/"):
            current_path = line[6:]
            changed.setdefault(current_path, set())
            next_new_line = None
            continue
        if line.startswith("@@"):
            next_new_line = hunk_start(line)
            continue
        if current_path is None or next_new_line is None:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            changed[current_path].add(next_new_line)
            next_new_line += 1
        elif not line.startswith("-"):
            next_new_line += 1
    return changed


def filter_diff_findings(
    findings: list[dict[str, Any]],
    *,
    changed_lines: set[int],
    added_file: bool,
) -> tuple[list[dict[str, Any]], int]:
    if added_file:
        return findings, 0
    kept: list[dict[str, Any]] = []
    suppressed = 0
    for finding in findings:
        finding_type = str(finding.get("type", ""))
        line = finding.get("line")
        if finding_type.startswith("source_file_"):
            suppressed += 1
            continue
        if finding_type.startswith("function_"):
            if isinstance(line, int) and line in changed_lines:
                kept.append(finding)
            else:
                suppressed += 1
            continue
        if isinstance(line, int) and line not in changed_lines:
            suppressed += 1
            continue
        kept.append(finding)
    return kept, suppressed


def add_finding(
    findings: list[dict[str, Any]],
    *,
    severity: str,
    type_: str,
    path: str,
    message: str,
    rule: str,
    line: int | None = None,
    recommendation: str = "",
    **extra: Any,
) -> None:
    item: dict[str, Any] = {
        "severity": severity,
        "type": type_,
        "path": path,
        "message": message,
        "rule": rule,
        "recommendation": recommendation,
    }
    if line is not None:
        item["line"] = line
    item.update(extra)
    findings.append(item)


def python_function_spans(lines: list[str]) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    for index, line in enumerate(lines):
        match = PY_FUNCTION_RE.match(line)
        if not match:
            continue
        indent = len(match.group("indent").replace("\t", "    "))
        end = len(lines)
        for next_index in range(index + 1, len(lines)):
            next_line = lines[next_index]
            if not next_line.strip() or next_line.lstrip().startswith(("#", "@")):
                continue
            next_indent = len(next_line) - len(next_line.lstrip(" "))
            if next_indent <= indent:
                end = next_index
                break
        spans.append((match.group("name"), index + 1, end))
    return spans


def c_like_name(match: re.Match[str]) -> str:
    return match.group("name") or match.group("arrow") or match.group("method") or "anonymous"


def brace_span_end(lines: list[str], start_index: int) -> int:
    depth = lines[start_index].count("{") - lines[start_index].count("}")
    end = start_index
    if depth <= 0:
        depth = 1 if "{" in lines[start_index] else 0
    for next_index in range(start_index + 1, len(lines)):
        depth += lines[next_index].count("{") - lines[next_index].count("}")
        end = next_index
        if depth <= 0:
            break
    return end


def c_like_function_spans(lines: list[str]) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    for index, line in enumerate(lines):
        match = JS_FUNCTION_RE.match(line)
        if not match:
            continue
        name = c_like_name(match)
        if name in CONTROL_NAMES:
            continue
        if "=>" in line and "{" not in line:
            spans.append((name, index + 1, index + 1))
            continue
        spans.append((name, index + 1, brace_span_end(lines, index) + 1))
    return spans


def function_spans(path: Path, lines: list[str]) -> list[tuple[str, int, int]]:
    if path.suffix == ".py":
        return python_function_spans(lines)
    return c_like_function_spans(lines)


def complexity(block: str) -> int:
    return 1 + len(CONTROL_FLOW_RE.findall(block))


def import_values(text: str) -> list[tuple[int, str]]:
    imports: list[tuple[int, str]] = []
    for match in IMPORT_RE.finditer(text):
        value = next((group for group in match.groups() if group), "")
        if not value:
            continue
        line = text.count("\n", 0, match.start()) + 1
        imports.append((line, value))
    return imports


def strip_string_literals(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        value = match.group(0)
        return "".join("\n" if char == "\n" else " " for char in value)

    return STRING_LITERAL_RE.sub(replace, text)

