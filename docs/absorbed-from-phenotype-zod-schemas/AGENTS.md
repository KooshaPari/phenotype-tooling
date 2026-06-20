# AGENTS.md

## Project Overview

`phenotype-zod-schemas` is the canonical Zod schema bundle for the Phenotype
fleet. It provides TypeScript-first runtime validators that are shared across
all frontends (Astro, Vite, Node CLIs) to enforce shape contracts at the
boundary between services, web UIs, and CI tooling.

## Stack

- Language: TypeScript (strict)
- Runtime: Node.js 18+
- Validator: `zod` v3
- Test runner: `vitest`
- Package manager: `bun`
- Build target: ESM (Node 18+)

## Key Commands

```bash
# Install dependencies
bun install --frozen-lockfile

# Type-check
bunx tsc --noEmit

# Run tests
bunx vitest run

# Lint
bunx biome check .
```

## File Map

- `src/index.ts` — re-exports the 5 common schemas (`Project`, `User`,
  `Status`, `DateRange`, `Pagination`)
- `src/schemas/` — individual schema definitions (one file per schema)
- `tests/` — vitest suites for each schema
- `tsconfig.json` — strict-mode TS config
- `package.json` — `bun`-managed, exports map for `@phenotype/zod-schemas`

## Quality Gate

```bash
task quality
```

Runs: install, typecheck, lint, test, and package export verification.

## Conventions

- All schemas are `z.object({...})` exported as both runtime + static types
  (via `z.infer<typeof Schema>`).
- New schemas must be added to `src/index.ts` exports AND to the package.json
  `exports` map.
- Tests live next to their schema in `tests/<schema>.test.ts`.
- Schemas are intentionally permissive: prefer `z.string().optional()` over
  `z.string().min(N)` to allow forward compatibility.

## Generated Code

This package is consumed as a library — never import from `./src/index.ts`
directly in downstream packages, always use `@phenotype/zod-schemas` (the
package name).
