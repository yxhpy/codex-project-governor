#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

RISK_TERMS = {
    "auth", "authentication", "authorization", "permission", "role", "rbac",
    "payment", "billing", "invoice", "refund", "checkout", "order",
    "security", "privacy", "pii", "secret", "token", "oauth", "session", "cookie",
    "migration", "schema", "database", "db", "data model", "webhook", "external api",
    "encryption", "production", "compliance", "rate limit", "concurrency", "lock",
    "delete", "destructive", "data loss", "rollback", "cache",
    "登录", "注册", "认证", "鉴权", "授权", "权限", "角色", "支付", "扣款", "退款",
    "订单", "账单", "安全", "隐私", "密钥", "令牌", "数据库", "迁移", "数据模型",
    "接口", "生产", "合规", "并发", "锁", "缓存", "删除", "数据丢失", "回滚",
}
REFACTOR_TERMS = {"refactor", "restructure", "rewrite", "cleanup", "reorganize", "extract", "split", "重构", "重写", "整理"}
UPGRADE_TERMS = {"upgrade", "update dependency", "bump", "version", "migrate to", "sdk", "framework", "release", "升级", "依赖", "版本", "迁移"}
RESEARCH_TERMS = {"research", "compare", "investigate", "evaluate", "调研", "研究", "对比", "评估"}
CLEAN_TERMS = {"clean", "reinstall", "refresh", "hygiene", "trash", "quarantine", "重装", "清理", "刷新"}
UI_TERMS = {
    "ui", "style", "component", "screen", "page", "layout", "button", "modal", "theme",
    "design", "dashboard", "widget", "css", "margin", "padding", "color", "font", "class",
    "页面", "样式", "组件", "间距", "颜色", "视觉", "设计",
}
TEST_TERMS = {"test", "spec", "coverage", "fixture", "mock", "test only", "add tests", "测试", "用例"}
DOCS_TERMS = {"docs", "documentation", "readme", "guide", "manual", "文档", "说明"}
BUG_TERMS = {"bug", "fix", "broken", "error", "crash", "regression", "修复", "错误", "失败", "崩溃"}
MICRO_TERMS = {"style", "css", "class", "margin", "padding", "spacing", "color", "font", "label", "copy", "typo", "text", "文案", "错别字", "颜色", "标题", "间距"}
GLOBAL_SHARED_TERMS = {"shared", "global", "common", "design token", "theme", "tokens", "components/ui", "design-system", "全局", "共享", "通用", "设计 token"}

NEGATIVE_PATTERNS = [
    ("do_not_change_api", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,32}(api|接口|contract|response|public contract)"),
    ("do_not_change_schema", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,36}(schema|database|db|数据表|数据库|模型)"),
    ("do_not_add_files", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,32}(new file|add file|新增文件|加文件|新文件)"),
    ("do_not_add_dependencies", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,32}(dependenc|package|library|npm|pip|依赖|包)"),
    ("do_not_change_global_style", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,32}(global style|theme|token|全局样式|主题|token)"),
    ("do_not_change_shared_components", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,32}(shared component|common component|共享组件|通用组件)"),
]


def load(path: Path | None, request: str | None) -> dict[str, Any]:
    if request:
        return {"request": request, "hints": {}}
    if path is None:
        text = sys.stdin.read().strip()
        if not text:
            return {"request": "", "hints": {}}
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return {"request": text, "hints": {}}
        return data if isinstance(data, dict) else {"request": str(data), "hints": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"request": data, "hints": {}} if isinstance(data, str) else data


def has_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def detect_negative_constraints(text: str) -> list[str]:
    return sorted({name for name, pattern in NEGATIVE_PATTERNS if re.search(pattern, text, flags=re.IGNORECASE)})


def strip_negative_constraints(text: str) -> str:
    stripped = text
    for _, pattern in NEGATIVE_PATTERNS:
        stripped = re.sub(pattern, " negative_constraint ", stripped, flags=re.IGNORECASE)
    return stripped


def neutralize_guardrail_terms(text: str, negative_constraints: list[str]) -> str:
    neutralized = text
    replacements = {
        "do_not_change_api": r"\b(api|contract|response|public contract)\b|接口|契约",
        "do_not_change_schema": r"\b(schema|database|db|data model|model)\b|数据表|数据库|模型",
        "do_not_add_dependencies": r"\b(dependenc\w*|package|library|npm|pip)\b|依赖|包",
    }
    for constraint, pattern in replacements.items():
        if constraint in negative_constraints:
            neutralized = re.sub(pattern, " guardrail ", neutralized, flags=re.IGNORECASE)
    return neutralized


def task_text(data: dict[str, Any]) -> str:
    hints = data.get("hints", {}) if isinstance(data.get("hints", {}), dict) else {}
    pieces = [
        str(data.get("request", data.get("user_request", ""))),
        " ".join(map(str, data.get("changed_areas", []))),
        " ".join(map(str, data.get("constraints", []))),
        " ".join(str(value) for value in hints.values()),
    ]
    return " ".join(pieces).lower()


def has_explicit_target(text: str, hints: dict[str, Any]) -> bool:
    if hints.get("target_file") or hints.get("target_files") or hints.get("target_page") or hints.get("target_component"):
        return True
    if re.search(r"[\w./-]+\.(tsx|ts|jsx|js|py|css|scss|md|vue|svelte|html|go|rs|json|yaml|yml|toml)", text, flags=re.IGNORECASE):
        return True
    return bool(re.search(r"(只改|only change|only modify|specified page|指定页面|目标文件|这个文件|this file)", text, flags=re.IGNORECASE))


def is_shared_or_global(text: str, hints: dict[str, Any]) -> bool:
    return bool(hints.get("target_is_shared_component") or hints.get("target_is_global_style") or has_any(text, GLOBAL_SHARED_TERMS))


def risk_signals(text: str) -> list[str]:
    negative_constraints = detect_negative_constraints(text)
    active = neutralize_guardrail_terms(strip_negative_constraints(text), negative_constraints)
    signals: list[str] = []
    groups = [
        ("risk_domain", RISK_TERMS),
        ("refactor_signal", REFACTOR_TERMS),
        ("upgrade_signal", UPGRADE_TERMS),
        ("research_signal", RESEARCH_TERMS),
        ("clean_signal", CLEAN_TERMS),
        ("ui_signal", UI_TERMS),
        ("test_signal", TEST_TERMS),
        ("docs_signal", DOCS_TERMS),
        ("bug_signal", BUG_TERMS),
    ]
    for label, terms in groups:
        if has_any(active, terms):
            signals.append(label)
    return signals


def compute_risk_score(text: str, hints: dict[str, Any], negative_constraints: list[str]) -> float:
    active = neutralize_guardrail_terms(strip_negative_constraints(text), negative_constraints)
    score = 0.0
    if has_any(active, RISK_TERMS):
        score += 0.42
    if any(term in active for term in ["auth", "oauth", "token", "session", "permission", "认证", "权限", "登录"]):
        score += 0.18
    if any(term in active for term in ["payment", "billing", "refund", "支付", "扣款", "退款"]):
        score += 0.22
    if any(term in active for term in ["schema", "database", "migration", "数据库", "迁移"]):
        score += 0.20
    if has_any(active, UPGRADE_TERMS):
        score += 0.16
    if has_any(active, REFACTOR_TERMS):
        score += 0.18
    if is_shared_or_global(text, hints):
        score += 0.12
    expected_modified = int(hints.get("expected_modified_files", 0) or 0)
    expected_added = int(hints.get("expected_added_files", 0) or 0)
    if expected_modified >= 8:
        score += 0.12
    if expected_added > 0:
        score += 0.08
    if negative_constraints:
        score += 0.04
    return round(max(0.0, min(0.99, score)), 2)


def compute_confidence(text: str, hints: dict[str, Any], risk_score: float, negative_constraints: list[str]) -> tuple[float, list[str]]:
    confidence = 0.56
    reasons: list[str] = []
    explicit_target = has_explicit_target(text, hints)
    micro_intent = has_any(text, MICRO_TERMS)
    exact_file_only = bool(hints.get("exact_file_only") or "only this file" in text or "只改这个文件" in text or "只改" in text)
    expected_modified = int(hints.get("expected_modified_files", 1 if explicit_target else 3) or 3)
    if explicit_target:
        confidence += 0.20
        reasons.append("Explicit target detected.")
    if micro_intent:
        confidence += 0.14
        reasons.append("Local style/copy/spacing intent detected.")
    if exact_file_only or expected_modified <= 1:
        confidence += 0.08
        reasons.append("Small file budget requested or inferred.")
    if negative_constraints:
        confidence += 0.04
        reasons.append("Negative constraints converted to guardrails.")
    if risk_score >= 0.45:
        confidence -= 0.22
        reasons.append("Risk score requires conservative route.")
    if is_shared_or_global(text, hints):
        confidence -= 0.15
        reasons.append("Shared/global impact detected.")
    return max(0.0, min(0.99, round(confidence, 2))), reasons


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
    if route in {"dependency_upgrade", "upgrade_or_migration"}:
        return {
            "max_files_changed": 8,
            "max_new_files": 3,
            "allow_dependencies": True,
            "allow_public_contract_changes": False,
            "allow_schema_changes": False,
            "allow_refactor": False,
            "requires_adr_or_pdr": True,
        }
    if lane == "fast_lane":
        return {"max_files_changed": 3, "max_new_files": 1, "allow_dependencies": False, "allow_public_contract_changes": False, "allow_schema_changes": False}
    if lane == "risk_lane":
        return {"max_files_changed": 10, "max_new_files": 4, "allow_dependencies": False, "allow_public_contract_changes": True, "allow_schema_changes": True, "requires_adr_or_pdr": True}
    if lane == "refactor_lane":
        return {"max_files_changed": 12, "max_new_files": 2, "allow_dependencies": False, "allow_public_contract_changes": False, "allow_schema_changes": False, "allow_refactor": True, "requires_adr_or_pdr": True}
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
        return ["direct-edit", "route-guard", "quality-gate", "evidence-manifest-lite"], [
            "context-pack-builder", "pattern-reuse-engine", "parallel-feature-builder", "test-first-synthesizer", "subagent-activation", "subagent-audit",
        ]
    if route in {"clean_reinstall_or_refresh"}:
        return ["clean-reinstall-manager", "context-indexer", "harness-doctor", "quality-gate"], ["parallel-feature-builder"]
    if route == "research":
        return ["session-lifecycle", "research-radar", "context-indexer", "version-researcher", "evidence-manifest"], []
    if route in {"dependency_upgrade", "upgrade_or_migration"}:
        return ["session-lifecycle", "version-researcher", "upgrade-advisor", "plugin-upgrade-migrator", "test-first-synthesizer", "quality-gate", "evidence-manifest", "merge-readiness"], []
    if route == "docs_only":
        return ["direct-edit", "quality-gate", "merge-readiness"], ["parallel-feature-builder", "subagent-audit", "test-first-synthesizer"]
    if route == "test_only":
        return ["context-indexer", "context-pack-builder", "direct-edit", "quality-gate", "evidence-manifest", "merge-readiness"], ["parallel-feature-builder"]
    if route == "risky_feature":
        return ["session-lifecycle", "context-indexer", "context-pack-builder", "pattern-reuse-engine", "test-first-synthesizer", "parallel-feature-builder", "quality-gate", "evidence-manifest", "merge-readiness"], []
    if route == "refactor":
        return ["session-lifecycle", "context-indexer", "context-pack-builder", "pattern-reuse-engine", "test-first-synthesizer", "parallel-feature-builder", "architecture-drift-check", "quality-gate", "evidence-manifest", "merge-readiness"], []
    return ["session-lifecycle", "context-indexer", "context-pack-builder", "pattern-reuse-engine", "test-first-synthesizer", "parallel-feature-builder", "quality-gate", "evidence-manifest", "merge-readiness"], []


def workflow_skills(items: list[str]) -> list[str]:
    skills: list[str] = []
    aliases = {"direct-edit": None, "evidence-manifest-lite": "evidence-manifest"}
    for item in items:
        item = aliases.get(item, item)
        if not item:
            continue
        if item.endswith("-quality-gate"):
            item = "quality-gate"
        if item not in skills:
            skills.append(item)
    return skills


def subagent_mode(route: str, quality: str, confidence: float, shared_or_global: bool) -> str:
    if route == "micro_patch" and confidence >= 0.82 and not shared_or_global:
        return "none"
    if route in {"docs_only", "test_only", "clean_reinstall_or_refresh"}:
        return "optional" if confidence < 0.70 else "none"
    if route in {"standard_feature", "ui_change", "bugfix", "risky_feature", "refactor", "dependency_upgrade", "upgrade_or_migration", "research"}:
        return "required" if quality == "strict" or confidence < 0.85 or route in {"standard_feature", "risky_feature", "refactor", "dependency_upgrade", "upgrade_or_migration", "research"} else "optional"
    return "optional"


def classify(data: dict[str, Any]) -> dict[str, Any]:
    hints = data.get("hints", {}) if isinstance(data.get("hints", {}), dict) else {}
    text = task_text(data)
    request = str(data.get("request", data.get("user_request", "")))
    negative_constraints = detect_negative_constraints(text)
    signals = risk_signals(text)
    risk_score = compute_risk_score(text, hints, negative_constraints)
    confidence, reasons = compute_confidence(text, hints, risk_score, negative_constraints)
    explicit_target = has_explicit_target(text, hints)
    micro_intent = has_any(text, MICRO_TERMS)
    shared_or_global = is_shared_or_global(text, hints)
    expected_modified = int(hints.get("expected_modified_files", 1 if explicit_target else 3) or 3)
    expected_added = int(hints.get("expected_added_files", 0) or 0)

    if "clean_signal" in signals:
        route, lane, quality, intent = "clean_reinstall_or_refresh", "standard_lane", "standard", "maintenance"
    elif "research_signal" in signals and "upgrade_signal" not in signals:
        route, lane, quality, intent = "research", "research_lane", "standard", "research"
    elif "upgrade_signal" in signals:
        route, lane, quality, intent = "dependency_upgrade", "risk_lane" if risk_score >= 0.45 else "standard_lane", "strict" if risk_score >= 0.45 else "standard", "upgrade"
    elif "docs_signal" in signals and risk_score < 0.35 and not set(signals) - {"docs_signal"}:
        route, lane, quality, intent = "docs_only", "fast_lane", "light", "docs"
    elif "test_signal" in signals and risk_score < 0.35 and not any(s in signals for s in ["upgrade_signal", "refactor_signal", "ui_signal"]):
        route, lane, quality, intent = "test_only", "fast_lane", "light", "test"
    elif explicit_target and micro_intent and risk_score < 0.35 and not shared_or_global and expected_modified <= 1 and expected_added == 0 and confidence >= 0.82:
        route, lane, quality, intent = "micro_patch", "fast_lane", "light", "micro_patch"
    elif "refactor_signal" in signals:
        route, lane, quality, intent = "refactor", "refactor_lane", "strict", "refactor"
    elif risk_score >= 0.45:
        route, lane, quality, intent = "risky_feature", "risk_lane", "strict", "feature_or_fix"
    elif micro_intent or shared_or_global:
        route, lane, quality, intent = "ui_change", "standard_lane", "standard", "ui_change"
    else:
        route, lane, quality, intent = "standard_feature", "standard_lane", "standard", "feature_or_fix"

    budget = route_budget(route, lane)
    required, skipped = workflow(route)
    guard = route_guard_requirements(route, budget, negative_constraints)
    evidence_required = route not in {"micro_patch", "docs_only", "clean_reinstall_or_refresh"} or quality == "strict"
    escalations = [
        "modified files exceed route budget",
        "new files added when not allowed",
        "shared/global component changed unexpectedly",
        "public API, schema, dependency, or style-system change required",
        "rewrite threshold exceeded",
        "quality gate fails after repair-loop limit",
    ]
    if evidence_required:
        escalations.append("evidence manifest is missing or incomplete")
    if quality in {"standard", "strict"}:
        escalations.append("tests cannot validate the change")

    return {
        "status": "classified",
        "router_version": "project-governor-harness-v6-router",
        "request": request,
        "intent": intent,
        "route": route,
        "lane": lane,
        "quality_level": quality,
        "quality_gate": quality,
        "confidence": confidence,
        "risk_score": risk_score,
        "risk_signals": signals,
        "negative_constraints": negative_constraints,
        "task_shape": {
            "explicit_target": explicit_target,
            "micro_intent": micro_intent,
            "shared_or_global": shared_or_global,
            "expected_modified_files": expected_modified,
            "expected_added_files": expected_added,
            "docs_only": route == "docs_only",
            "test_only": route == "test_only",
        },
        "subagent_mode": subagent_mode(route, quality, confidence, shared_or_global),
        "required_skills": workflow_skills(required),
        "required_workflow": required,
        "skipped_workflow": skipped,
        "change_budget": budget,
        "route_guard_requirements": guard,
        "evidence_required": evidence_required,
        "escalate_if": escalations,
        "escalation_triggers": escalations,
        "reasons": reasons or ["Defaulted to Harness v6 safe standard workflow."],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify a task for Project Governor Harness v6.0.")
    parser.add_argument("input", type=Path, nargs="?")
    parser.add_argument("--request")
    args = parser.parse_args()
    print(json.dumps(classify(load(args.input, args.request)), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
