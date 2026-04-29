from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

CATALOG_SCHEMA = "project-governor-skill-catalog-v1"
ALLOWED_VISIBILITIES = {"primary", "workflow", "internal", "advanced", "deprecated"}
ALLOWED_CONSOLIDATION_STATUSES = {"resolved"}
DOC_GROUP_VISIBILITIES = {"recommended": {"primary", "workflow"}, "internal": {"internal"}, "advanced": {"advanced"}}
README_GROUP_SECTIONS = {
    "README.md": {
        "recommended": ("### Recommended entry points", "### Internal workflow stages"),
        "internal": ("### Internal workflow stages", "### Advanced and diagnostic tools"),
        "advanced": ("### Advanced and diagnostic tools", "## Install locally for yourself"),
    },
    "README.zh-CN.md": {
        "recommended": ("### 推荐入口", "### 内部工作流阶段"),
        "internal": ("### 内部工作流阶段", "### 高级和诊断工具"),
        "advanced": ("### 高级和诊断工具", "## 安装到个人 Codex"),
    },
}


def parse_frontmatter(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    metadata: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def issue(severity: str, kind: str, message: str, **extra: Any) -> dict[str, Any]:
    row = {"severity": severity, "type": kind, "message": message}
    row.update(extra)
    return row


def catalog_names(entries: list[dict[str, Any]]) -> set[str]:
    return {str(entry.get("name")) for entry in entries if entry.get("name")}


def catalog_shape_issues(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    if catalog.get("schema") != CATALOG_SCHEMA:
        return [
            issue(
                "error",
                "catalog_schema_mismatch",
                "Skill catalog schema is not recognized.",
                expected=CATALOG_SCHEMA,
                actual=catalog.get("schema"),
            )
        ]
    return []


def duplicate_entry_issues(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    names = [entry.get("name") for entry in entries]
    counts = Counter(name for name in names if name)
    return [
        issue("error", "duplicate_catalog_entry", "Skill catalog has duplicate entries.", skill=name)
        for name, count in sorted(counts.items())
        if count > 1
    ]


def directory_coverage_issues(entries: list[dict[str, Any]], actual_names: set[str]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    names = catalog_names(entries)
    for name in sorted(actual_names - names):
        issues.append(issue("error", "missing_catalog_entry", "Skill directory is missing from skills/CATALOG.json.", skill=name))
    for name in sorted(names - actual_names):
        issues.append(issue("error", "extra_catalog_entry", "Skill catalog entry has no matching skill directory.", skill=name))
    return issues


def catalog_entry_issues(project: Path, entry: dict[str, Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    name = str(entry.get("name", ""))
    visibility = entry.get("visibility")
    if visibility not in ALLOWED_VISIBILITIES:
        issues.append(issue("error", "invalid_visibility", "Skill catalog visibility is invalid.", skill=name, visibility=visibility))
    if not entry.get("category"):
        issues.append(issue("error", "missing_category", "Skill catalog entry is missing a category.", skill=name))
    if len(str(entry.get("summary", ""))) < 20:
        issues.append(issue("warning", "short_summary", "Skill catalog summary is too short to be useful.", skill=name))

    skill_md = project / "skills" / name / "SKILL.md"
    metadata = parse_frontmatter(skill_md)
    if not metadata:
        issues.append(issue("error", "missing_skill_frontmatter", "SKILL.md frontmatter is missing or unreadable.", skill=name, path=str(skill_md)))
    elif metadata.get("name") != name:
        issues.append(issue("error", "frontmatter_name_mismatch", "SKILL.md frontmatter name does not match directory/catalog name.", skill=name, frontmatter_name=metadata.get("name")))
    return issues


def valid_skill_name_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) >= 2 and all(isinstance(item, str) for item in value)


def valid_optional_string_list(value: Any) -> bool:
    return not value or (isinstance(value, list) and all(isinstance(item, str) for item in value))


def consolidation_group_object_issues(
    group: dict[str, Any], index: int, known_names: set[str]
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    name = str(group.get("name", ""))
    if not name:
        issues.append(issue("error", "missing_consolidation_group_name", "Catalog consolidation group is missing a name.", index=index))
    if group.get("status") not in ALLOWED_CONSOLIDATION_STATUSES:
        issues.append(issue("error", "invalid_consolidation_group_status", "Catalog consolidation group status is invalid.", group=name, status=group.get("status")))
    skills = group.get("skills")
    if not valid_skill_name_list(skills):
        issues.append(issue("error", "invalid_consolidation_group_skills", "Catalog consolidation group skills must list at least two skill names.", group=name))
        return issues
    unknown = sorted(set(skills) - known_names)
    if unknown:
        issues.append(issue("error", "unknown_consolidation_group_skill", "Catalog consolidation group references unknown skills.", group=name, skills=unknown))
    if not valid_optional_string_list(group.get("candidate_types", [])):
        issues.append(issue("error", "invalid_consolidation_group_candidate_types", "Catalog consolidation group candidate_types must be a list of strings.", group=name))
    return issues


def consolidation_group_issues(entries: list[dict[str, Any]], groups: Any) -> list[dict[str, Any]]:
    if groups is None:
        return []
    if not isinstance(groups, list):
        return [issue("error", "invalid_consolidation_groups", "Catalog consolidation_groups must be a list.")]

    known_names = catalog_names(entries)
    issues: list[dict[str, Any]] = []
    for index, group in enumerate(groups):
        if isinstance(group, dict):
            issues.extend(consolidation_group_object_issues(group, index, known_names))
        else:
            issues.append(issue("error", "invalid_consolidation_group", "Catalog consolidation group must be an object.", index=index))
    return issues


def expected_readme_groups(entries: list[dict[str, Any]]) -> dict[str, set[str]]:
    groups = {group: set() for group in DOC_GROUP_VISIBILITIES}
    for entry in entries:
        name = str(entry.get("name", ""))
        visibility = entry.get("visibility")
        for group, values in DOC_GROUP_VISIBILITIES.items():
            if name and visibility in values:
                groups[group].add(name)
    return groups


def markdown_section(text: str, start_marker: str, end_marker: str) -> str | None:
    start = text.find(start_marker)
    if start < 0:
        return None
    content_start = start + len(start_marker)
    end = text.find(end_marker, content_start)
    if end < 0:
        return None
    return text[content_start:end]


def mentioned_catalog_skills(section: str, known_names: set[str]) -> set[str]:
    return {name for name in re.findall(r"`([^`]+)`", section) if name in known_names}


def readme_group_issues(project: Path, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expected = expected_readme_groups(entries)
    known_names = set().union(*expected.values()) if expected else set()
    issues: list[dict[str, Any]] = []
    for rel_path, sections in README_GROUP_SECTIONS.items():
        path = project / rel_path
        if not path.exists():
            issues.append(issue("error", "readme_file_missing", "README skill grouping file is missing.", path=str(path)))
            continue
        text = path.read_text(encoding="utf-8")
        for group, (start, end) in sections.items():
            section = markdown_section(text, start, end)
            if section is None:
                issues.append(issue("error", "readme_skill_group_section_missing", "README skill grouping section is missing.", path=rel_path, group=group))
                continue
            actual = mentioned_catalog_skills(section, known_names)
            missing = sorted(expected[group] - actual)
            extra = sorted(actual - expected[group])
            if missing:
                issues.append(issue("error", "readme_skill_group_missing", "README skill group is missing catalog skills.", path=rel_path, group=group, skills=missing))
            if extra:
                issues.append(issue("error", "readme_skill_group_extra", "README skill group contains skills from a different catalog visibility group.", path=rel_path, group=group, skills=extra))
    return issues


def find_issues(project: Path, catalog: dict[str, Any], entries: list[dict[str, Any]], actual_names: set[str]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    issues.extend(catalog_shape_issues(catalog))
    issues.extend(duplicate_entry_issues(entries))
    issues.extend(directory_coverage_issues(entries, actual_names))
    for entry in entries:
        issues.extend(catalog_entry_issues(project, entry))
    issues.extend(consolidation_group_issues(entries, catalog.get("consolidation_groups")))
    issues.extend(readme_group_issues(project, entries))
    return issues
