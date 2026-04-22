#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


RISK = {
    "auth",
    "authentication",
    "authorization",
    "permission",
    "role",
    "rbac",
    "payment",
    "billing",
    "invoice",
    "security",
    "privacy",
    "pii",
    "migration",
    "schema",
    "database",
    "db",
    "data model",
    "webhook",
    "integration",
    "external api",
    "oauth",
    "token",
    "secret",
    "认证",
    "授权",
    "权限",
    "支付",
    "账单",
    "安全",
    "隐私",
    "数据库",
    "迁移",
    "数据模型",
    "接口",
}
REFACTOR = {"refactor", "restructure", "rewrite", "cleanup", "reorganize", "extract", "split", "重构", "重写"}
UPGRADE = {"upgrade", "update dependency", "bump", "version", "migrate to", "sdk", "framework", "升级", "依赖", "版本"}
UI = {
    "ui",
    "style",
    "component",
    "screen",
    "page",
    "layout",
    "button",
    "modal",
    "theme",
    "design",
    "dashboard",
    "widget",
    "css",
    "margin",
    "padding",
    "color",
    "font",
    "class",
    "页面",
    "样式",
    "组件",
    "间距",
    "颜色",
}
TEST = {"test", "spec", "coverage", "fixture", "mock", "test only", "add tests", "测试"}
DOCS = {"docs", "documentation", "readme", "guide", "manual", "文档", "说明"}
BUG = {"bug", "fix", "broken", "error", "crash", "regression", "修复", "错误", "失败"}
MICRO = {"style", "css", "class", "margin", "padding", "spacing", "color", "font", "label", "copy", "typo", "text", "样式", "间距", "文案", "错别字", "颜色", "标题"}
GLOBAL_SHARED = {"shared", "global", "common", "design token", "theme", "tokens", "button", "modal", "layout", "全局", "共享", "通用", "设计 token"}

NEGATIVE_PATTERNS = [
    ("do_not_change_api", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,24}(api|接口|contract|response)"),
    ("do_not_change_schema", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,30}(schema|database|db|数据表|数据库|模型)"),
    ("do_not_add_files", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,24}(new file|add file|新增文件|加文件|新文件)"),
    ("do_not_add_dependencies", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,24}(dependenc|package|library|npm|pip|依赖|包)"),
    ("do_not_change_global_style", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,24}(global style|theme|token|全局样式|主题|token)"),
    ("do_not_change_shared_components", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,24}(shared component|common component|共享组件|通用组件)"),
]


def load(path: Path | None, request: str | None) -> dict[str, Any]:
    if request:
        return {"request": request, "hints": {}}
    if path is None:
        text = sys.stdin.read().strip()
        if not text:
            return {"request": ""}
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return {"request": text, "hints": {}}
        return data if isinstance(data, dict) else {"request": str(data), "hints": {}}

    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, str):
        return {"request": data, "hints": {}}
    return data


def has_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def detect_negative_constraints(text: str) -> list[str]:
    found = [name for name, pattern in NEGATIVE_PATTERNS if re.search(pattern, text, flags=re.IGNORECASE)]
    return sorted(set(found))


def strip_negative_constraints(text: str) -> str:
    stripped = re.sub(
        r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,48}(api|接口|contract|response|schema|database|db|数据表|数据库|模型|dependency|package|library|依赖|包|global style|theme|token|全局样式|共享组件|通用组件)",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    for _, pattern in NEGATIVE_PATTERNS:
        stripped = re.sub(pattern, " ", stripped, flags=re.IGNORECASE)
    return stripped


def task_text(data: dict[str, Any]) -> str:
    hints = data.get("hints", {}) if isinstance(data.get("hints", {}), dict) else {}
    pieces = [
        str(data.get("request", "")),
        " ".join(map(str, data.get("changed_areas", []))),
        " ".join(map(str, data.get("constraints", []))),
        " ".join(str(value) for value in hints.values()),
    ]
    return " ".join(pieces).lower()


def has_explicit_target(text: str, hints: dict[str, Any]) -> bool:
    if hints.get("target_file") or hints.get("target_files") or hints.get("target_page") or hints.get("target_component"):
        return True
    if re.search(r"[\w./-]+\.(tsx|ts|jsx|js|py|css|scss|md|vue|svelte|html)", text, flags=re.IGNORECASE):
        return True
    return bool(re.search(r"(只改|only change|only modify|specified page|指定页面|目标文件|这个文件)", text, flags=re.IGNORECASE))


def is_shared_or_global(text: str, hints: dict[str, Any]) -> bool:
    return bool(hints.get("target_is_shared_component") or hints.get("target_is_global_style") or has_any(text, GLOBAL_SHARED))


def active_risk(text: str) -> bool:
    return has_any(strip_negative_constraints(text), RISK)


def risk_signals(text: str, risk: bool) -> list[str]:
    signals: list[str] = []
    if risk:
        signals.append("risk_domain")
    groups = [
        ("refactor_signal", REFACTOR),
        ("upgrade_signal", UPGRADE),
        ("ui_signal", UI),
        ("test_signal", TEST),
        ("docs_signal", DOCS),
        ("bug_signal", BUG),
    ]
    signals.extend(label for label, terms in groups if has_any(text, terms))
    return signals


def route_budget(route: str, lane: str) -> dict[str, Any]:
    if route == "micro_patch":
        return {
            "max_files_changed": 1,
            "max_new_files": 0,
            "allow_dependencies": False,
            "allow_public_contract_changes": False,
            "allow_schema_changes": False,
            "allow_refactor": False,
            "allow_global_style_changes": False,
            "allow_shared_component_changes": False,
            "allow_new_components": False,
            "requires_adr_or_pdr": False,
        }
    if route == "dependency_upgrade":
        return {
            "max_files_changed": 6,
            "max_new_files": 2,
            "allow_dependencies": True,
            "allow_public_contract_changes": False,
            "allow_schema_changes": False,
            "requires_adr_or_pdr": True,
        }
    if lane == "fast_lane":
        return {"max_files_changed": 3, "max_new_files": 1, "allow_dependencies": False, "allow_public_contract_changes": False, "allow_schema_changes": False}
    if lane == "risk_lane":
        return {"max_files_changed": 8, "max_new_files": 3, "allow_dependencies": False, "allow_public_contract_changes": True, "allow_schema_changes": True, "requires_adr_or_pdr": True}
    if lane == "refactor_lane":
        return {"max_files_changed": 10, "max_new_files": 2, "allow_dependencies": False, "allow_public_contract_changes": False, "allow_schema_changes": False, "allow_refactor": True, "requires_adr_or_pdr": True}
    return {"max_files_changed": 8, "max_new_files": 3, "allow_dependencies": False, "allow_public_contract_changes": False, "allow_schema_changes": False}


def route_guard_requirements(route: str, budget: dict[str, Any], negative_constraints: list[str]) -> dict[str, Any]:
    guard = {
        "route": route,
        "max_modified_files": budget.get("max_files_changed", 9999),
        "max_added_files": budget.get("max_new_files", 9999),
        "allow_dependencies": bool(budget.get("allow_dependencies", False)),
        "allow_api_changes": bool(budget.get("allow_public_contract_changes", False)),
        "allow_schema_changes": bool(budget.get("allow_schema_changes", False)),
        "allow_new_components": bool(budget.get("allow_new_components", True)),
        "allow_global_style_changes": bool(budget.get("allow_global_style_changes", True)),
        "allow_shared_component_changes": bool(budget.get("allow_shared_component_changes", True)),
        "allow_rewrite": bool(budget.get("allow_refactor", False)),
        "max_repair_rounds": 3,
        "negative_constraints": negative_constraints,
        "must_stop_if_budget_exceeded": True,
    }
    if "do_not_change_api" in negative_constraints:
        guard["allow_api_changes"] = False
    if "do_not_change_schema" in negative_constraints:
        guard["allow_schema_changes"] = False
    if "do_not_add_files" in negative_constraints:
        guard["max_added_files"] = 0
    if "do_not_add_dependencies" in negative_constraints:
        guard["allow_dependencies"] = False
    if "do_not_change_global_style" in negative_constraints:
        guard["allow_global_style_changes"] = False
    if "do_not_change_shared_components" in negative_constraints:
        guard["allow_shared_component_changes"] = False
    return guard


def workflow(route: str) -> tuple[list[str], list[str]]:
    if route == "micro_patch":
        return ["direct-edit", "route-guard", "light-quality-gate"], [
            "context-pack-builder",
            "pattern-reuse-engine",
            "parallel-feature-builder",
            "test-first-synthesizer",
            "subagent-audit",
        ]
    if route == "dependency_upgrade":
        return ["version-researcher", "upgrade-advisor", "iteration-planner", "quality-gate", "merge-readiness"], []
    if route == "docs_only":
        return ["direct-edit", "quality-gate", "merge-readiness"], ["parallel-feature-builder", "subagent-audit"]
    if route == "test_only":
        return ["context-pack-builder", "direct-edit", "quality-gate", "merge-readiness"], ["parallel-feature-builder"]
    if route == "risky_feature":
        return ["iteration-planner", "context-pack-builder", "pattern-reuse-engine", "test-first-synthesizer", "parallel-feature-builder", "quality-gate", "merge-readiness"], []
    return ["context-pack-builder", "pattern-reuse-engine", "test-first-synthesizer", "parallel-feature-builder", "quality-gate", "merge-readiness"], []


def workflow_skills(workflow_items: list[str]) -> list[str]:
    skills: list[str] = []
    for item in workflow_items:
        if item == "direct-edit":
            continue
        if item.endswith("-quality-gate"):
            item = "quality-gate"
        if item not in skills:
            skills.append(item)
    return skills


def classify(data: dict[str, Any]) -> dict[str, Any]:
    hints = data.get("hints", {}) if isinstance(data.get("hints", {}), dict) else {}
    text = task_text(data)
    request = str(data.get("request", ""))
    negative_constraints = detect_negative_constraints(text)
    risk = active_risk(text)
    explicit_target = has_explicit_target(text, hints)
    micro_intent = has_any(text, MICRO)
    shared_or_global = is_shared_or_global(text, hints)
    expected_modified = int(hints.get("expected_modified_files", 1 if explicit_target else 3))
    expected_added = int(hints.get("expected_added_files", 0))
    exact_file_only = bool(hints.get("exact_file_only") or "only this file" in text or "只改这个文件" in text or "只改" in text)

    confidence = 0.55
    reasons: list[str] = []
    if explicit_target:
        confidence += 0.22
        reasons.append("Explicit target detected.")
    if micro_intent:
        confidence += 0.18
        reasons.append("Local style/copy/spacing intent detected.")
    if exact_file_only or expected_modified <= 1:
        confidence += 0.08
        reasons.append("Small file budget requested or inferred.")
    if negative_constraints:
        confidence += 0.04
        reasons.append("Negative constraints converted to guardrails.")
    if risk:
        confidence -= 0.35
        reasons.append("Active high-risk surface detected.")
    if shared_or_global:
        confidence -= 0.25
        reasons.append("Shared/global component or style impact detected.")
    if expected_added > 0:
        confidence -= 0.10
        reasons.append("New files expected.")
    confidence = max(0.0, min(0.99, round(confidence, 2)))

    signals = risk_signals(text, risk)
    if explicit_target and micro_intent and not risk and not shared_or_global and expected_modified <= 1 and expected_added == 0 and confidence >= 0.85:
        route, lane, quality = "micro_patch", "fast_lane", "light"
    elif "docs_signal" in signals and not risk and not set(signals) - {"docs_signal"}:
        route, lane, quality = "docs_only", "fast_lane", "light"
    elif "test_signal" in signals and not risk and not any(signal in signals for signal in ["upgrade_signal", "refactor_signal", "ui_signal"]):
        route, lane, quality = "test_only", "fast_lane", "light"
    elif "upgrade_signal" in signals:
        route, lane, quality = "dependency_upgrade", "risk_lane" if risk else "standard_lane", "strict" if risk else "standard"
    elif "refactor_signal" in signals:
        route, lane, quality = "refactor", "refactor_lane", "strict"
    elif risk:
        route, lane, quality = "risky_feature", "risk_lane", "strict"
    elif "bug_signal" in signals and len(text.split()) <= 18:
        route, lane, quality = "tiny_patch", "fast_lane", "light"
    elif "ui_signal" in signals or micro_intent or shared_or_global:
        route, lane, quality = "ui_change", "standard_lane", "standard"
    else:
        route, lane, quality = "standard_feature", "standard_lane", "standard"

    budget = route_budget(route, lane)
    required, skipped = workflow(route)
    guard = route_guard_requirements(route, budget, negative_constraints)
    return {
        "status": "classified",
        "request": request,
        "route": route,
        "lane": lane,
        "quality_level": quality,
        "quality_gate": quality,
        "confidence": confidence,
        "risk_signals": signals,
        "negative_constraints": negative_constraints,
        "required_skills": workflow_skills(required),
        "required_workflow": required,
        "skipped_workflow": skipped,
        "change_budget": budget,
        "route_guard_requirements": guard,
        "escalate_if": [
            "modified files exceed route budget",
            "new files added when not allowed",
            "shared/global component changed unexpectedly",
            "public API, schema, dependency, or style-system change required",
            "rewrite threshold exceeded",
            "quality gate fails after repair-loop limit",
        ],
        "escalation_triggers": [
            "modified files exceed route budget",
            "new files added when not allowed",
            "shared/global component changed unexpectedly",
            "API/schema/dependency/style-system change required",
            "rewrite threshold exceeded",
            "tests cannot validate the change",
        ],
        "reasons": reasons or ["Defaulted to safe standard workflow."],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, nargs="?")
    parser.add_argument("--request")
    args = parser.parse_args()
    print(json.dumps(classify(load(args.input, args.request)), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
