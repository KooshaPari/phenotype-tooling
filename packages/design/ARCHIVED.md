# Moved: `@phenotype/design`

The design system package formerly lived at `packages/design/` in this repository.
It has been consolidated into the canonical **phenoDesign** repository.

## Canonical source

- **Repository:** https://github.com/KooshaPari/phenoDesign
- **Package name:** `@phenotype/design`

## Depend on phenoDesign

```json
{
  "dependencies": {
    "@phenotype/design": "github:KooshaPari/phenoDesign"
  }
}
```

For local monorepo development:

```json
{
  "dependencies": {
    "@phenotype/design": "file:../phenoDesign"
  }
}
```

## Absorbed assets

Unique assets merged into phenoDesign include:

- `css/glass.css` — per-OS glassmorphism utilities
- `docs/guide/glass-recipe.md` — glass recipe specification
- Typed `glass` and `typography` token exports

Do not re-add `packages/design/` here. Update consumers to depend on phenoDesign directly.
