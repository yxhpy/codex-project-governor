---
name: research-radar
description: Research candidate capabilities, ecosystem changes, and implementation options before Project Governor adopts them; rank evidence, relevance, risk, and user choices without modifying code.
---

# Research Radar

## Purpose

Turn new ideas, ecosystem changes, official documentation, changelogs, and competing-agent patterns into a concise, evidence-backed recommendation before implementation.

Use this skill when the user asks about:

- the next version of Project Governor
- whether to adopt a new Codex capability
- comparing Claude, Letta, Hermes, OpenClaw, or other agent patterns
- researching a library, framework, governance rule, memory pattern, or subagent workflow
- deciding whether a feature belongs in the current iteration, a spike, a future release, or should be rejected

## Core rule

Research first. Do not implement, upgrade, rewrite, or modify manifests until the user chooses an option.

Always show:

1. what was researched
2. source quality and evidence level
3. which findings match the current project needs
4. which findings are experimental, risky, or unstable
5. recommendation: `adopt_now`, `spike`, `watch`, or `reject`
6. why the recommendation was made
7. next user choices

## Source policy

Prefer sources in this order:

1. official documentation
2. official changelogs or release notes
3. standards, specs, or research papers
4. project repository docs
5. vendor blogs
6. community posts only as supporting signals, never as the only basis for a decision

If online research is unavailable, say that the run is offline and use only local docs, release notes, and user-provided evidence.

## Automatic Subagent Activation

Run `subagent-activation` with workflow `research-radar` when research is broad, evidence is unclear, or multiple options must be compared.

Spawn selected read-only subagents for broad research:

1. `context-scout`: find local docs, relevant skills, templates, scripts, and examples.
2. `risk-scout`: identify breaking changes, sandbox/security implications, and unsupported platforms.
3. `docs-memory-reviewer`: identify documentation, memory, ADR/PDR, and research artifact requirements.
4. `quality-reviewer`: consolidate evidence into adoption choices and blocking risks.

Each subagent must:

- avoid writing files
- cite evidence or include source URLs/paths
- distinguish confirmed facts from inference
- identify uncertainty
- recommend one of `adopt_now`, `spike`, `watch`, or `reject`

## Deterministic helper

Use the helper when you have structured candidates:

```bash
python3 skills/research-radar/scripts/score_research_candidates.py \
  --manifest examples/research-candidates.json \
  --need memory \
  --need subagents \
  --need research
```

## Write policy

When the user asks for a research artifact, write only to:

- `docs/research/`
- `reports/research/`
- `tasks/<date>-<slug>/RESEARCH_BRIEF.md`

Do not modify application code, package manifests, lockfiles, hooks, or rules during research.
