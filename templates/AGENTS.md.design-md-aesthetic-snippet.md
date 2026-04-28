## DESIGN.md aesthetic gate for UI work

For any task that creates or edits user-facing UI, frontend routes, React/Next.js components, Tailwind/CSS, design tokens, layouts, pages, dashboards, landing pages, settings pages, forms, tables, modals, navigation, or responsive behavior:

1. Use `$design-md-aesthetic-governor` before editing files.
2. Verify Gemini/Stitch design-service configuration from shell environment variables or project-root `.env-design`.
3. Read the whole `DESIGN.md` file and summarize the applicable tokens and rationale.
4. Run:

   ```bash
   python3 "${PROJECT_GOVERNOR_ROOT:-.}/skills/design-md-aesthetic-governor/scripts/design_md_gate.py" preflight --task "<current task>"
   ```

5. Do not edit UI files until `.codex/design-md-governor/read-proof.json` exists and matches the current `DESIGN.md` hash.
6. If `.env-design` is missing or incomplete, stop UI work and ask the user to fill `GEMINI_BASE_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, and `STITCH_MCP_API_KEY`, unless shell environment variables already provide them or the user intentionally sets `DESIGN_BASIC_MODE=1` for basic mode. `STITCH_MCP_URL` defaults to `https://stitch.googleapis.com/mcp`.
7. If `DESIGN.md` is missing, stop UI coding and create `docs/design/DESIGN_MD_ADOPTION_PLAN.md` instead of inventing styling.
8. Use `VoltAgent/awesome-design-md` references only as aesthetic inspiration. Do not copy protected logos, brand names, assets, or exact visual identity unless explicitly authorized.
9. After edits, run:

   ```bash
   python3 "${PROJECT_GOVERNOR_ROOT:-.}/skills/design-md-aesthetic-governor/scripts/verify_design_usage.py"
   ```

10. In full-service mode, use Stitch MCP for visual prototype exploration and Gemini for design critique when the task asks for prototype, redesign, or visual review. In basic mode, skip those services and rely on GPT/Codex plus local DESIGN.md checks.
11. The final response for UI work must include a `DESIGN.md compliance` section with design mode, design-service configuration status, the read proof path, aesthetic reference, lint status, drift status, and token changes.
