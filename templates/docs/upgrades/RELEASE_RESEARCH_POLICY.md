# Release Research Policy

Run version research before upgrade-advisor when a dependency, framework, tool, SDK, runtime, or Project Governor version may change.

## Required release fields

- installed version
- candidate version
- skipped versions
- major/minor/patch distance
- evidence quality
- relevant changes
- breaking changes
- migration steps
- risks
- recommendation
- user choices

## Safety

No upgrade may edit manifests, lockfiles, CI config, hooks, rules, or application code until the user chooses an upgrade path.
