Use @project-governor clean-reinstall-manager.

Goal:
Cleanly reinstall the user-level Project Governor plugin and refresh initialized projects without polluting project directories.

Rules:
- If the current directory is not a Project Governor project, stop and list all discovered governed projects.
- If the current directory is the Project Governor plugin root, stop and do not quarantine plugin-owned files.
- Let the user choose ignore, all, or selected projects.
- If inside a project, generate a refresh plan.
- Do not overwrite project customizations.
- Regenerate missing project-owned governance files from templates.
- Merge missing markdown sections when safe.
- Move plugin-global noise to `.project-governor/trash/<timestamp>/` by default.
- Do not delete trash unless explicitly requested.
- Never overwrite memory or decision files.
