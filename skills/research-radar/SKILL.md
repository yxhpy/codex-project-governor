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

## Subagent workflow

When the user explicitly asks for subagents, delegation, or parallel research, spawn read-only subagents for broad research:

1. `official-docs-researcher`: read official docs, changelogs, and feature maturity notes.
2. `compatibility-risk-researcher`: identify breaking changes, sandbox/security implications, and unsupported platforms.
3. `implementation-fit-researcher`: map each finding to Project Governor's existing skills, templates, and scripts.
4. `alternative-pattern-researcher`: compare Claude, Letta, Hermes, OpenClaw, or other relevant systems when requested.
5. `roadmap-synthesizer`: consolidate evidence into release candidates and user choices.

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
