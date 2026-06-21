# Iconography Standard

Implements the [phenotype-infra iconography standard](https://github.com/kooshapari/phenotype-infra/blob/main/docs/governance/iconography-standard.md).

The Paginary docs UI ships icons in three visual styles, all converging on the
same accessibility and color contract.

## Styles

| Style           | Rendering                  | Used in                              |
|-----------------|----------------------------|--------------------------------------|
| **Fluent**      | 1.5px stroke, geometric    | `apps/handbook/`, `apps/specs/`      |
| **Material**    | Filled + outlined, 24×24   | `apps/journeys/` (journey viewer UI) |
| **Liquid Glass**| 24×24, blur 8px, white 70% | `apps/xdd/`, marketing pages         |

## Contract

Every icon, regardless of style, must:

- Be a 24×24 SVG.
- Use `currentColor` for fill/stroke (no hard-coded colors).
- Declare `role="img"` and an `aria-label` (or `aria-hidden="true"` if decorative).
- Live under the appropriate style subdir (e.g. `apps/journeys/src/content/icons/fluent/`).
- Export a named React/Vue component via the package's index (one barrel per style).

## Source

Icons are NOT authored in this repo. The canonical source is
[`phenotype-icons`](https://github.com/kooshapari/phenotype-icons) (a separate
package). Paginary consumes it via:

```ts
// apps/journeys/src/content/npm/journey-viewer/src/icons.ts
import { Fluent as F, Material as M, Liquid as L } from '@phenotype/icons';
```

When adding a new icon:

1. Add the SVG to `phenotype-icons/<style>/<icon-name>.svg`.
2. Run the generator (`pnpm run generate`) to produce the typed barrel.
3. Re-export from the relevant app's `icons.ts` if scoped.

## Status

- [x] Define the three style families (Fluent / Material / Liquid Glass)
- [x] Lock the 24×24 + `currentColor` + a11y contract
- [x] Establish `@phenotype/icons` as the canonical source
- [ ] First 10 icons per style migrated to `phenotype-icons`
- [ ] Add visual regression test (`apps/specs/src/content/operations/iconography/snap.test.ts`)
