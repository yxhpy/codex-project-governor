Use $version-researcher.

Research candidate versions before upgrade-advisor is used.

Rules:
- Advisory only.
- Show current version, candidate versions, skipped versions, evidence quality, relevant changes, breaking/migration risk, request match, and recommendation.
- Prefer official changelogs, release notes, migration guides, security advisories, and EOL/deprecation policies.
- Do not modify manifests, lockfiles, application code, CI config, hooks, or rules.
- Ask the user to choose whether to keep, research more, preview in isolation, plan an upgrade iteration, apply after confirmation, or pin/reject.
