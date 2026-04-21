# Research Policy

Use research before adopting new capabilities, libraries, workflows, agent patterns, or governance rules.

## Source priority

1. Official documentation
2. Official changelogs / release notes
3. Official migration guides
4. Security advisories / EOL policies
5. Standards / RFCs / research papers
6. Maintainer blogs
7. Third-party analysis
8. Community reports, only as supporting signals

## Required classification

Every candidate must be classified as:

- `adopt_now`
- `spike`
- `watch`
- `reject`

## Required fields

- candidate
- source quality
- matched project needs
- risk
- maturity
- recommendation
- reason
- user choice

## Write boundary

Research may update `docs/research/`, `reports/research/`, or task research briefs. Research must not modify application code, dependency manifests, lockfiles, hooks, or rules.
