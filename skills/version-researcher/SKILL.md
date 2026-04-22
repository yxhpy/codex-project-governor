---
name: version-researcher
description: Research candidate release versions before upgrade decisions, automatically activating read-only release/risk/docs subagents when multiple versions or unclear evidence are involved.
---

# Version Researcher

## Purpose

Turn release information into a structured, auditable research brief before any upgrade is planned or applied.

This skill is advisory only. It must not edit manifests, lockfiles, application code, or install packages.

## Automatic Subagent Activation

When multiple versions, unclear evidence, security risk, migration risk, or project-wide impact exists, run `subagent-activation` with workflow `version-researcher`.

Spawn selected read-only subagents, wait for all results, and consolidate evidence before `upgrade-advisor` is used.

## Use when

- The user asks whether the next version is worth researching.
- The user asks what changed between the installed version and newer versions.
- The user asks which newer versions are relevant to a current feature request.
- `upgrade-advisor` lacks enough evidence to make a recommendation.
- A dependency, tool, framework, or this plugin itself may need an upgrade.

## Required evidence order

Prefer primary sources:

1. Official release notes or changelog
2. Official migration guide
3. Official security advisory / CVE / GHSA
4. Official deprecation or EOL policy
5. Official issue / PR / RFC
6. Maintainer blog post
7. High-quality third-party analysis
8. Community reports

If primary sources are unavailable, say so and lower the confidence.

## Research workflow

1. Identify the installed version.
2. Identify candidate versions.
3. Collect release evidence for skipped versions when practical.
4. Compute major/minor/patch distance and skipped versions.
5. Map changes to the user's current request and project needs.
6. Classify each candidate as `required`, `recommended`, `consider`, `preview_in_isolation`, `defer`, or `pin`.
7. Explain why, using evidence.
8. Present choices before any upgrade action.

## Required output

Produce a table with:

- package/tool/plugin
- current version
- candidate version
- version distance
- skipped versions
- evidence quality
- relevant changes
- project/request match
- breaking/migration risk
- recommendation
- why

Then ask the user to choose one of:

- keep current version
- research another candidate version
- preview upgrade in isolated branch/worktree
- create an upgrade iteration plan
- apply upgrade only after explicit confirmation
- pin/reject this version

## Safety rules

- Do not run package manager install commands.
- Do not modify `package.json`, lockfiles, plugin manifests, app code, or CI config.
- Do not rely on community comments when official changelogs exist.
- Do not recommend major-version upgrades inline with unrelated feature work.
- High-risk or breaking upgrades must be isolated as their own iteration.
- Security fixes that affect the installed version should be flagged as urgent, but still require explicit confirmation before modification.

## Deterministic helper

When a local release research manifest is available, run:

```bash
python3 skills/version-researcher/scripts/research_versions.py --manifest examples/version-research-manifest.json --request "<user request>"
```
