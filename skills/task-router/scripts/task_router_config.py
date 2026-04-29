#!/usr/bin/env python3
from __future__ import annotations

import re

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
AUTH_RISK_TERMS = {"auth", "oauth", "token", "session", "permission", "认证", "权限", "登录"}
PAYMENT_RISK_TERMS = {"payment", "billing", "refund", "支付", "扣款", "退款"}
DATA_RISK_TERMS = {"schema", "database", "migration", "数据库", "迁移"}
RISK_SCORE_GROUPS = (
    (RISK_TERMS, 0.42),
    (AUTH_RISK_TERMS, 0.18),
    (PAYMENT_RISK_TERMS, 0.22),
    (DATA_RISK_TERMS, 0.20),
    (UPGRADE_TERMS, 0.16),
    (REFACTOR_TERMS, 0.18),
)
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
DOC_TARGET_RE = re.compile(r"\b(readme|changelog|license|contributing|agents\.md|claude\.md)\b", re.IGNORECASE)
DOCS_ONLY_BLOCKING_SIGNALS = {"risk_domain", "refactor_signal", "upgrade_signal", "research_signal", "clean_signal", "ui_signal", "test_signal"}
PRODUCTION_CHANGE_RE = re.compile(
    r"\b(add|create|implement|build|change|update)\s+(?:an?\s+|the\s+)?"
    r"(?!tests?\b)(helper|utility|service|component|endpoint|feature|parser|export|api|hook|schema|workflow|command|script)\b",
    re.IGNORECASE,
)
DOC_PACKS = {
    "micro_patch": {"primary_roles": ["agent_instructions"], "max_initial_docs": 1, "max_sections": 3, "max_total_chars_first": 12_000, "memory_search": False},
    "docs_only": {"primary_roles": ["doc", "agent_instructions", "governance_history"], "max_initial_docs": 3, "max_sections": 8, "max_total_chars_first": 40_000, "memory_search": False},
    "test_only": {"primary_roles": ["test", "code", "conventions"], "max_initial_docs": 2, "max_sections": 8, "max_total_chars_first": 50_000, "memory_search": True},
    "standard_feature": {"primary_roles": ["agent_instructions", "conventions", "test", "code", "quality"], "max_initial_docs": 4, "max_sections": 10, "max_total_chars_first": 80_000, "memory_search": True},
    "ui_change": {"primary_roles": ["design", "ui_or_component", "conventions", "test"], "max_initial_docs": 4, "max_sections": 10, "max_total_chars_first": 80_000, "memory_search": True},
    "risky_feature": {"primary_roles": ["agent_instructions", "decision", "quality", "test", "security", "auth", "payment", "data_model"], "max_initial_docs": 8, "max_sections": 16, "max_total_chars_first": 140_000, "memory_search": True},
    "refactor": {"primary_roles": ["architecture", "decision", "conventions", "test", "quality"], "max_initial_docs": 8, "max_sections": 14, "max_total_chars_first": 120_000, "memory_search": True},
    "dependency_upgrade": {"primary_roles": ["governance_history", "decision", "quality", "test", "data_model"], "max_initial_docs": 8, "max_sections": 14, "max_total_chars_first": 140_000, "memory_search": True},
    "upgrade_or_migration": {"primary_roles": ["governance_history", "decision", "quality", "test", "data_model"], "max_initial_docs": 8, "max_sections": 14, "max_total_chars_first": 140_000, "memory_search": True},
    "research": {"primary_roles": ["doc", "decision", "memory", "task_history", "governance_history"], "max_initial_docs": 10, "max_sections": 18, "max_total_chars_first": 160_000, "memory_search": True},
    "clean_reinstall_or_refresh": {"primary_roles": ["agent_instructions", "governance_history", "quality"], "max_initial_docs": 5, "max_sections": 10, "max_total_chars_first": 80_000, "memory_search": True},
}
NEGATIVE_PATTERNS = [
    ("do_not_change_api", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,32}(api|接口|contract|response|public contract)"),
    ("do_not_change_schema", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,36}(schema|database|db|数据表|数据库|模型)"),
    ("do_not_add_files", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,32}(new file|add file|新增文件|加文件|新文件)"),
    ("do_not_add_dependencies", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,32}(dependenc|package|library|npm|pip|依赖|包)"),
    ("do_not_change_global_style", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,32}(global style|theme|token|全局样式|主题|token)"),
    ("do_not_change_shared_components", r"(do not|don't|dont|no|without|不要|不准|不能|别).{0,32}(shared component|common component|共享组件|通用组件)"),
]
