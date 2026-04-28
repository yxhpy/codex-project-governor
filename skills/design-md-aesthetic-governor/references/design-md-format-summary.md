# DESIGN.md format summary

A DESIGN.md file has two layers:

1. YAML front matter with machine-readable design tokens.
2. Markdown sections with human-readable rationale and usage guidance.

The token values are normative; prose explains why and how to apply them.

Recommended token groups:

- `colors`
- `typography`
- `spacing`
- `rounded`
- `components`

Recommended section order:

1. Overview / Brand & Style
2. Colors
3. Typography
4. Layout / Layout & Spacing
5. Elevation & Depth / Elevation
6. Shapes
7. Components
8. Do's and Don'ts

Common CLI commands:

```bash
npx @google/design.md lint DESIGN.md
npx @google/design.md diff DESIGN.before.md DESIGN.md
npx @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json
npx @google/design.md spec --rules
```
