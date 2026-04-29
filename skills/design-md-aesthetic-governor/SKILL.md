---
name: design-md-aesthetic-governor
description: Mandatory UI/frontend coding gate for Codex. Use for React, Next.js, Tailwind, CSS, page, component, dashboard, landing page, redesign, visual polish, responsive layout, design system, theme, or any task that changes user-facing UI. Forces Codex to verify Gemini/Stitch design-service configuration, read DESIGN.md, optionally select an awesome-design-md aesthetic reference, lint tokens, create read proof, implement only from tokens/rationale, and verify no design drift.
---

# DESIGN.md Aesthetic Governor

This skill governs user-facing UI work. It is not a generic frontend helper. Its job is to prevent Codex from improvising visual language.

## Activation

Use this skill for any task that edits or creates:

- React, Next.js, Vue, Svelte, Astro, Remix, or frontend route files
- `*.tsx`, `*.jsx`, `*.css`, `*.scss`, `tailwind.config.*`, theme files, style modules, component libraries
- pages, components, layouts, cards, forms, tables, modals, nav, dashboards, landing pages, settings pages
- copy that affects UI hierarchy, CTA prominence, visual density, empty/error/loading states

Do not use this skill for backend-only work, pure tests unrelated to UI, data migrations, or infrastructure tasks.

## Non-negotiable workflow

Before editing UI files, Codex must complete the following sequence.

### 1. Verify design-service configuration

Before UI review or prototyping, the project must provide Gemini and Stitch credentials through shell environment variables or a project-root `.env-design` file.

Required keys:

```dotenv
GEMINI_BASE_URL=
GEMINI_API_KEY=
GEMINI_MODEL=
GEMINI_PROTOCOL=auto
STITCH_MCP_URL=https://stitch.googleapis.com/mcp
STITCH_MCP_API_KEY=
```

Environment variables with those names take precedence. The aliases `DESIGN_GEMINI_BASE_URL`, `DESIGN_GEMINI_API_KEY`, `DESIGN_GEMINI_MODEL`, `DESIGN_GEMINI_PROTOCOL`, `DESIGN_STITCH_MCP_URL`, and `DESIGN_STITCH_MCP_API_KEY` are also accepted. `GEMINI_PROTOCOL` may be `auto`, `openai`, or `gemini`; `openai` means OpenAI-compatible chat completions, and `gemini` means native Gemini `generateContent`. For native Gemini through a gateway, `GEMINI_BASE_URL` must be the gateway's Gemini protocol root, such as `https://host/gemini` when the provider serves `/gemini/v1beta`. `STITCH_MCP_URL` defaults to `https://stitch.googleapis.com/mcp`.

To use basic mode without Gemini/Stitch service configuration, the user must set `DESIGN_BASIC_MODE=1` either as a shell environment variable or in the project-root `.env-design` file. Legacy bypass variables `DESIGN_ENV_SKIP=1` and `DESIGN_SERVICE_CONFIG_SKIP=1` are also accepted from either source. `.env-design` is preferred when Codex hooks or Windows processes may not inherit shell variables set after startup; keep it local and uncommitted.

Run:

```bash
python3 "${PROJECT_GOVERNOR_ROOT:-.}/skills/design-md-aesthetic-governor/scripts/design_env_check.py" --write-template
```

If required values are missing and basic mode is not enabled, this writes a blank `.env-design` template and blocks. The file is local secret configuration and must not be committed. Reports may record which source supplied each key, but must never record API key values.

Project-level MCP configuration may use the same environment variable without storing the key:

```json
{
  "mcpServers": {
    "stitch": {
      "url": "https://stitch.googleapis.com/mcp",
      "headers": {
        "X-Goog-Api-Key": "${STITCH_MCP_API_KEY}"
      }
    }
  }
}
```

The hosted Stitch MCP endpoint is the default path and does not require local `stitch-mcp`, `npm`, or `gcloud` setup. If a project deliberately replaces it with a local MCP server, install that server as part of the project-specific setup before running full-service UI work.

### 1.1 Choose full-service or basic mode

Full-service mode:

1. GPT/Codex reads the task, repository rules, `DESIGN.md`, and current UI code.
2. Stitch MCP is used for visual prototyping or screen-level design exploration when the user asks for a prototype, redesign, or visual direction. The default transport is remote streamable HTTP at `https://stitch.googleapis.com/mcp`.
3. Gemini is used as an external design reviewer for visual rationale, UI critique, and consistency checks against `DESIGN.md`.
4. GPT/Codex converts the accepted design direction into repository-native code, tests, and governance evidence.
5. Local scripts verify `DESIGN.md` read proof and drift before final delivery.

Use the service scripts to make this repeatable:

```bash
python3 "${PROJECT_GOVERNOR_ROOT:-.}/skills/design-md-aesthetic-governor/scripts/design_service_smoke.py" --task "<connectivity smoke>"
python3 "${PROJECT_GOVERNOR_ROOT:-.}/skills/design-md-aesthetic-governor/scripts/design_service_review.py" --task "<current UI task>"
```

`design_service_smoke.py` verifies that Gemini and Stitch are reachable. `design_service_review.py` sends the current task plus `DESIGN.md` summary to Gemini, initializes Stitch MCP, lists available Stitch tools, and writes `.codex/design-md-governor/service-review.json` plus `.codex/design-md-governor/SERVICE_REVIEW.md`. It must not create remote Stitch projects unless a separate project-specific tool flow explicitly requests that action.

Basic mode:

1. GPT/Codex still reads `DESIGN.md` and current UI code.
2. No Stitch MCP or Gemini calls are required.
3. Codex may implement frontend work using project components, local DESIGN.md tokens, bundled lint, and drift checks.
4. Final answers must state that design services ran in `basic` mode.

Do not let Stitch or Gemini directly replace project-owned `DESIGN.md`. Their output is advisory; GPT/Codex must translate accepted ideas into project-owned tokens, rationale, and code.

### 2. Locate design source

Check for, in order:

1. `DESIGN.md` at the repository root.
2. A closer directory-specific `DESIGN.md` in the current working path.
3. Existing project design docs under `docs/design/`, `styleguide/`, or `design/`.
4. If no usable design source exists, do not begin UI coding. Create `docs/design/DESIGN_MD_ADOPTION_PLAN.md` and ask for adoption or choose a temporary aesthetic reference only when the user explicitly authorizes it.

### 3. Read and summarize DESIGN.md

Read the whole file, not just the front matter. Extract:

- brand mood and anti-mood
- colors and semantic roles
- typography hierarchy
- spacing, radius, elevation, shape language
- component rules
- responsive behavior
- do/don't constraints
- any agent prompt guide or implementation notes

Run from the governed repository root. If Project Governor is installed outside this repository, set `PROJECT_GOVERNOR_ROOT=/path/to/codex-project-governor` first.

```bash
python3 "${PROJECT_GOVERNOR_ROOT:-.}/skills/design-md-aesthetic-governor/scripts/design_md_gate.py" preflight --task "<current user task>"
```

This writes `.codex/design-md-governor/read-proof.json`. Do not modify UI files until this file exists and matches the current `DESIGN.md` hash.

Prefer the official Google CLI when available:

```bash
npx @google/design.md lint DESIGN.md
```

Use the bundled Python linter as fallback:

```bash
python3 "${PROJECT_GOVERNOR_ROOT:-.}/skills/design-md-aesthetic-governor/scripts/design_md_lint.py" DESIGN.md
```

### 4. If style is underspecified, choose inspiration from awesome-design-md

Use the curated aesthetic catalog as inspiration, not as blind brand copying.

Run:

```bash
python3 "${PROJECT_GOVERNOR_ROOT:-.}/skills/design-md-aesthetic-governor/scripts/select_aesthetic.py" --task "<current user task and product context>"
```

Pick at most 1 primary aesthetic and 1 secondary reference. Write the choice into the implementation plan. Examples:

- Vercel / Linear: precision, developer SaaS, monochrome, low-noise.
- Supabase / VoltAgent: dark technical product, green accent, code-first.
- Stripe / Revolut: fintech precision, gradient cards, trust and motion.
- Notion / Mintlify: documentation, productivity, soft editorial surfaces.
- Apple / Airbnb: consumer premium, spacious, photography or lifestyle led.

Never use protected logos, exact brand names in UI copy, or proprietary assets unless the project already owns them or the user explicitly instructs it. Borrow visual grammar and token structure, not brand identity.

### 5. Generate implementation plan before code

Create or update `.codex/design-md-governor/implementation-plan.md` with:

- files to edit
- components to create/change
- state matrix: loading, empty, success, error, long-content, mobile
- tokens from DESIGN.md that will be used
- design mode: `full_service` or `basic`
- Gemini/Stitch configuration source check, without secret values when in full-service mode
- aesthetic reference, if any
- anti-patterns avoided
- verification commands

### 6. Code under token discipline

Rules while coding:

- Use semantic HTML first.
- Use project components before inventing new atoms.
- Use tokens from `DESIGN.md` and existing theme config.
- Do not add arbitrary Tailwind colors such as `bg-blue-500`, `text-purple-600`, `from-pink-500`, unless they are explicitly mapped to DESIGN.md tokens.
- Do not hardcode raw hex colors in UI files unless the exact value exists in DESIGN.md.
- Do not introduce new radius, shadow, spacing, font, or animation systems without updating `DESIGN.md` first.
- Do not remove loading, empty, error, disabled, permission, or responsive states.
- Keep primary CTA hierarchy aligned with the design rationale.

### 7. Verify design usage after edits

Run:

```bash
python3 "${PROJECT_GOVERNOR_ROOT:-.}/skills/design-md-aesthetic-governor/scripts/verify_design_usage.py"
```

If the official CLI is available, also run:

```bash
npx @google/design.md lint DESIGN.md
```

If `DESIGN.md` changed, compare before/after:

```bash
npx @google/design.md diff DESIGN.before.md DESIGN.md
```

or use the project's existing diff script if present.

### 7. Required final answer section

Every UI task final response must include:

```md
## DESIGN.md compliance
- Design services configured: yes/no
- Design mode: full_service/basic
- Design source read: yes/no
- Read proof: .codex/design-md-governor/read-proof.json
- Aesthetic reference: <none | preset id + rationale>
- Lint: pass/fail
- Drift check: pass/fail
- Any token changes: yes/no
```

If any required gate failed, say `NOT SHIPPED` and list the failing gate.

## Missing setup behavior

If Gemini/Stitch design-service configuration is missing and basic mode is not enabled, do not begin UI review, prototyping, or UI coding. Run `design_env_check.py --write-template`, ask the user to fill `.env-design`, and stop until all required values are present, shell environment variables provide them, or the user intentionally sets `DESIGN_BASIC_MODE=1` in the shell environment or project `.env-design`.

## Missing DESIGN.md behavior

If no `DESIGN.md` exists, do not silently style the UI. Instead:

1. Generate `docs/design/DESIGN_MD_ADOPTION_PLAN.md`.
2. Recommend 3 aesthetic presets from the catalog.
3. Explain the token implications.
4. Wait for explicit user approval before creating `DESIGN.md` or using one preset as temporary style source.

## Relationship to the two upstream projects

- Google `design.md` provides the formal file structure: YAML front matter for machine-readable tokens plus Markdown rationale for human-readable design guidance.
- `awesome-design-md` provides a curated collection of DESIGN.md style references inspired by real developer-focused and product brands.

This skill turns those sources into Codex behavior: read, lint, summarize, prove, code, verify.
