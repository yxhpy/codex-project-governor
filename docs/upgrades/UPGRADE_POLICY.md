# Upgrade Policy

Upgrades are iterative changes, not background maintenance work that silently changes the project.

## Default rule

Do not upgrade dependencies, tools, SDKs, runtimes, framework versions, or governance plugin versions without an explicit upgrade decision.

## Advisory phase

Before upgrading, run an upgrade advisory pass that reports:

- current version
- candidate version
- major/minor/patch distance
- number of skipped releases when known
- whether the candidate is needed by the current user request
- security, EOL, compatibility, migration, style, and architecture risks
- tests required to validate the upgrade
- recommended user choice

## User choices

Every proposed upgrade must be classified into one of these choices:

- `upgrade_now`: safe or required, and directly relevant to the current task
- `plan_upgrade_iteration`: useful but large enough to require a separate task
- `defer`: not needed for the current task or too risky right now
- `reject_or_pin`: conflicts with project constraints or should remain pinned

## Required approval

An explicit approval is required when an upgrade:

- changes a major version
- changes a framework, runtime, compiler, database, API client, auth provider, payment provider, or design system
- introduces breaking changes
- requires migrations
- modifies public API contracts
- changes UI/component patterns
- affects build, test, lint, deploy, or CI behavior

## Evidence requirements

An upgrade decision must include:

- why the upgrade is needed
- what request or risk it addresses
- alternatives considered
- known migration risks
- validation plan
- rollback plan
- decision owner or reviewer when available

## Implementation rule

After approval, create a normal `tasks/<date>-<slug>/ITERATION_PLAN.md` before modifying manifests or lockfiles.
