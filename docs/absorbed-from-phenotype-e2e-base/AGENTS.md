# AGENTS.md — phenotype-e2e-base

## Project Overview

`phenotype-e2e-base` is the canonical end-to-end testing harness for the
Phenotype org's web frontends (landing pages, dashboards). Built on
Playwright + TypeScript with the Bun runtime.

It owns:
- Cross-browser visual regression suite
- Per-landing-page spec files (one per `sites/*` in `phenotype-landing`)
- Shared test fixtures (auth, navigation, accessibility helpers)

## Stack

- **Runtime:** Bun 1.x
- **Test runner:** Playwright Test
- **Browsers:** Chromium, Firefox, WebKit (Playwright-managed)
- **Types:** TypeScript 5.x

## Key Commands

```bash
# Install (downloads Playwright browsers)
bun install

# Run full E2E suite
bun run test

# Run single spec
bunx playwright test tests/byteport.spec.ts

# Update visual snapshots (after intentional UI changes)
bunx playwright test --update-snapshots

# Open HTML report from last run
bunx playwright show-report
```

## File Map

| Path | Purpose |
|------|---------|
| `tests/` | Playwright test specs (one per landing site) |
| `fixtures/` | Test fixtures (auth, navigation, a11y helpers) |
| `playwright.config.ts` | Playwright config — browser matrix, timeouts, base URLs |
| `package.json` | Bun workspace declaration; depends on `phenotype-zod-schemas` |
| `tsconfig.json` | TypeScript strict mode |
| `bun.lock` | Bun lockfile (committed for reproducibility) |

## Quality Gate

```bash
# Full gate (matches CI)
task quality
```

The Taskfile recipes run install → typecheck → lint → test in order and
fail-fast on any error.

## CI

- `.github/workflows/ci.yml` — runs install, typecheck, lint, test on
  every PR to main. Uploads Playwright HTML report as artifact.
- See `STATUS.md` for current stage coverage.

## Notes

- This repo is a TEST harness — the production code under test lives in
  other repos (e.g. `phenotype-landing`, `BytePort`, `PhenoKits`).
- Snapshots should be reviewed on every PR; `--update-snapshots` is a
  manual operation gated on visual review of the diff.
- Test against deployed URLs in CI; against `localhost` for local dev.
