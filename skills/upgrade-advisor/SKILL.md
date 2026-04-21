---
name: upgrade-advisor
description: Use this skill when a user wants to know whether dependencies, tools, Codex governance files, or project conventions should be upgraded before implementing a request.
---

# Upgrade Advisor

## Purpose

Give the user an evidence-based upgrade menu before changing versions.

This skill is advisory by default. It must first show what is outdated, how far behind it is, which upgrades are relevant to the user's current requirement, and why an upgrade is or is not recommended.

## Default behavior

Do not upgrade automatically.
Do not edit package manifests.
Do not install packages.
Do not run migrations.
Do not rewrite code for a new version.

The output must first present choices for the user:

- upgrade now
- plan upgrade as a separate iteration
- defer
- reject / pin current version

Only after the user explicitly chooses an upgrade path may implementation continue, and that implementation must go through `iteration-planner`.

## Read first

- `AGENTS.md`
- `docs/conventions/ITERATION_CONTRACT.md`
- `docs/conventions/CONVENTION_MANIFEST.md`
- `docs/upgrades/UPGRADE_POLICY.md`
- `docs/upgrades/UPGRADE_REGISTER.md`
- relevant manifests such as `package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`
- relevant lockfiles

## When to use

Use this skill when:

- the user asks whether to upgrade libraries, frameworks, tools, SDKs, or the Project Governor plugin
- a requested feature may require a newer version
- a dependency is far behind current releases
- an upgrade may unlock a requested capability
- security, EOL, compatibility, or migration risk is relevant
- Codex is about to add a dependency but an existing dependency could be upgraded instead

## Subagent pattern

For existing projects, spawn read-only subagents when the upgrade surface is non-trivial:

1. `version-inventory-agent`: inspect manifests and lockfiles; list current versions and package scopes.
2. `need-match-agent`: map the user's requested feature or fix to libraries that may need newer versions.
3. `risk-agent`: inspect migration guides, breaking changes, config changes, and peer dependency risk.
4. `test-impact-agent`: identify tests and smoke checks needed for each possible upgrade.
5. `style-architecture-agent`: check whether the upgrade would introduce new patterns, APIs, or visual drift.

Each subagent must be read-only and must include evidence paths or source links.

## Required report

The report must include:

| Package | Current | Candidate | Behind / isolated by | Requirement relevance | Risk | Recommendation | Why |
|---|---:|---:|---:|---|---|---|---|

Definitions:

- `Behind / isolated by` should include major/minor/patch distance when semver is available.
- If a list of available versions is available, also show how many releases would be skipped.
- `Requirement relevance` should say whether the upgrade is required, likely useful, optional, or unrelated to the current user request.
- `Recommendation` must be one of: `upgrade_required`, `recommend_upgrade`, `consider_upgrade`, `defer`, `reject_or_pin`.

## Recommendation policy

Recommend `upgrade_required` when:

- a security issue is present
- current version is EOL or unsupported
- the requested feature explicitly requires a newer version
- compatibility with another already-approved dependency requires it

Recommend `recommend_upgrade` when:

- the upgrade directly unlocks the user's requested capability
- risk is low or medium
- tests and migration surface are clear

Recommend `consider_upgrade` when:

- the upgrade is useful but not necessary for the current request
- it reduces future maintenance risk
- it should be planned separately

Recommend `defer` when:

- the version is behind but unrelated to the request
- the migration is high-risk
- the project lacks tests to validate the upgrade
- the upgrade would cause style, architecture, or API drift

Recommend `reject_or_pin` when:

- a newer version conflicts with the project's architecture or product constraints
- the dependency should be replaced, removed, or kept pinned
- the upgrade requires a redesign that the user did not request

## Deterministic helper

Use the bundled helper when upgrade candidates have been collected into JSON:

```bash
python3 skills/upgrade-advisor/scripts/analyze_upgrade_candidates.py examples/upgrade-candidates.json
```

The helper is offline. It does not call registries. For real latest-version analysis, collect current/latest/available-version evidence first, then feed it to the helper.

## Output rules

- Separate facts from assumptions.
- Explain why each recommended upgrade matters for the current request.
- Do not hide high migration risk.
- Prefer smaller target upgrades when they satisfy the requirement.
- If latest version evidence is missing, say that the project is only comparing against provided candidate versions.
- If upgrading is approved, create an iteration plan before changing files.
