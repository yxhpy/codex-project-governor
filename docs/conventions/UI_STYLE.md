# UI Style

This repository does not ship a UI implementation.

## Confirmed Facts

- No `src/`, `app/`, `components/`, stylesheet, or UI runtime tree exists in this repository.
- The only obvious visual asset is `assets/icon.png`.
- UI and component conventions exist as downstream governance templates, not as local application components.

## Rules

- Do not introduce a UI framework, component library, styling system, or design-token system without an ADR.
- If a future UI is added, create project-specific UI conventions here before or alongside the implementation.
- Keep template UI guidance under `templates/docs/conventions/` generic unless the change is explicitly about downstream template defaults.

## Evidence

- `README.md`
- `assets/icon.png`
- `templates/docs/conventions/UI_STYLE.md`
- `templates/docs/conventions/COMPONENT_REGISTRY.md`
