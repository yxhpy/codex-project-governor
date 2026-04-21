---
name: memory-compact
description: Compact recent project activity into durable, auditable project memory for scheduled maintenance, release retrospectives, or long Codex sessions.
---

# Memory Compact

## Purpose

Convert recent activity into durable project memory without storing speculation as fact.

## Read first

- `AGENTS.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/memory/PROJECT_MEMORY.md`
- `docs/memory/OPEN_QUESTIONS.md`
- `docs/memory/REPEATED_AGENT_MISTAKES.md`
- `docs/memory/RISK_REGISTER.md`
- recent `tasks/*/RETRO.md`
- recent `tasks/*/EXECUTION_LOG.md`
- recent `docs/decisions/*.md`
- recent PR review comments if available
- recent CI or release reports if available

## Classification

Classify every candidate as:

- `durable_fact`
- `decision`
- `open_question`
- `repeated_mistake`
- `risk`
- `stale_item`
- `temporary_note`
- `secret_or_sensitive`
- `ignore`

## Write rules

- Do not write guesses as facts.
- Do not store secrets.
- Do not erase decision history.
- Mark outdated facts as `superseded`; do not delete them.
- Every new memory item must include evidence.
- Prefer small patches.
- If confidence is low, write to `OPEN_QUESTIONS.md`, not `PROJECT_MEMORY.md`.
- If a repeated mistake should become a rule, update `AGENTS.md` only with concise behavior guidance.
- Do not modify application code.

## Deterministic helper

Use:

```bash
python3 skills/memory-compact/scripts/classify_memory_items.py <json-or-text-input>
```

## Output

Return:

1. summary of findings
2. files updated
3. memory items added
4. items rejected
5. questions needing human review
