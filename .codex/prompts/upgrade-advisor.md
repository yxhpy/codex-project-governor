Use $upgrade-advisor.

Analyze whether this project should upgrade any dependency, tool, SDK, framework, runtime, or Project Governor governance asset before implementing the requested change.

Rules:
- Advisory only. Do not edit manifests, lockfiles, application code, or governance files.
- Show current version, candidate version, semantic distance, and skipped release count when known.
- Explain which candidates are required or useful for the user's current request.
- Recommend one of: upgrade_required, recommend_upgrade, consider_upgrade, defer, reject_or_pin.
- Present user choices: upgrade_now, plan_upgrade_iteration, defer, reject_or_pin.
- If an upgrade is approved later, route it through iteration-planner before implementation.
