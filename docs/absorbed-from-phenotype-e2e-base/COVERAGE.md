# Playwright Test Coverage — Concept

This document defines **what "test coverage" means in `phenotype-e2e-base`**,
how it is measured, and how the harness enforces it. It is the conceptual
counterpart to the auto-generated `COVERAGE_REPORT.md` matrix.

> If you only need to know which cells are currently covered, read
> `COVERAGE_REPORT.md`. If you need to know *why* we model coverage this
> way, *how to add a new flow*, or *how this integrates with the
> Playwright project matrix*, read this document.

---

## 1. Why a coverage model at all?

`phenotype-e2e-base` is a Playwright E2E harness for **5 landing pages**
(`byteport`, `phenokits`, `agileplus`, `projects`, `kooshapari`),
running against **3 browser engines** (chromium, firefox, webkit).

Without an explicit model:

- It is trivial to silently drop a landing page from the suite.
- It is impossible to tell whether `projects.spec.ts` covers the
  *hero CTA* or just *footer year* without opening the file.
- "Is the suite green?" gives no signal about *which flows* regressed
  when a spec is deleted.
- Cross-browser coverage is implicit and easy to forget.

The coverage model treats these gaps as **first-class artifacts**: a
declarative matrix of what *should* be tested, a scanner that discovers
what *is* being tested, and a generator that emits a diff (the report).

---

## 2. The coverage cell

A **cell** is the atomic unit of coverage:

> **cell = (site, flow)**

- **site** — a landing page under test. One of the `sites[]` in
  `coverage-suite/coverage.config.ts`.
- **flow** — a user journey or component check on that site. Currently:
  - `hero-cta` — primary call-to-action is visible and well-formed.
  - `github-stats` — the GitHub stats card renders.
  - `footer-year` — footer contains the current year.
  - `nav-links` — header nav is present and links are clickable.
  - `a11y-baseline` — `axe` / Playwright a11y assertions pass.

A cell has three statuses:

| Status | Meaning |
|--------|---------|
| **covered** | A spec exists for the site AND it contains a test that maps to the flow AND the spec runs on every required browser project. |
| **partial** | The spec exists and contains the test, but does not run on all required browser projects (rare — usually means someone disabled a project locally). |
| **missing** | No spec for the site, or the spec has no test that maps to this flow. |

Total coverage is `covered / required` (excluding `partial` cells).
A `partial` cell is treated as **not fully covered** for the headline
percentage, but is listed in the Gaps section so it is not silent.

---

## 3. How a spec maps to a cell

The generator scans `tests/*.spec.ts`. The mapping is **filename-driven**
and **test-name-driven**:

1. **Site** is derived from the spec file name:
   `tests/byteport.spec.ts` → site `byteport`.
2. **Flow** is derived from each `test("…")` name inside the file, by
   substring match against the canonical flow ids:

   | Test name contains… | Maps to flow |
   |----------------------|--------------|
   | `hero`, `cta`        | `hero-cta`   |
   | `github`, `stats`    | `github-stats` |
   | `footer`, `year`     | `footer-year` |
   | `nav`, `links`, `menu` | `nav-links` |
   | `a11y`, `accessib`, `axe` | `a11y-baseline` |

3. **Browser coverage** is inherited from `playwright.config.ts` —
   every spec runs on every project in the active matrix
   (`chromium`, `firefox`, `webkit`) unless a test is annotated with
   `@only` / `@skip` (Playwright built-ins).

This means **adding a flow is as simple as writing a test whose name
matches one of the substring patterns**. No registry to update, no
annotations to invent.

---

## 4. The required matrix

`coverage-suite/coverage.config.ts` declares what *must* be covered. Each
entry binds a `(site, flow)` pair to the set of Playwright projects
required to exercise it:

```ts
{ site: "byteport", flow: "hero-cta",
  requiredProjects: ["chromium", "firefox", "webkit"] }
```

Most flows are required on all 3 browsers (browser-rendering
inconsistencies are the #1 source of regressions in landing pages).
A few are required only on `chromium` to keep CI cost down:

- `byteport.a11y-baseline` — `axe` runs in one browser, then we trust it.
- `*.nav-links` (non-byteport) — visual nav is the only place where
  cross-browser divergence matters; the rest is a single-browser
  smoke check.

This matrix is **deliberate**. Adding a row is a contract that someone
must keep green. Removing a row is a coverage regression and must be
justified in the PR.

---

## 5. Outputs

Running `bun run coverage` produces two artifacts:

### `coverage.json` — machine-readable

```jsonc
{
  "generatedAt": "2026-06-12T…",
  "totals": { "required": 19, "covered": 12, "partial": 0, "missing": 7, "percentCovered": 63 },
  "sites": [...],
  "projects": ["chromium", "firefox", "webkit"],
  "cells": [
    { "site": "byteport", "flow": "hero-cta",
      "requiredProjects": ["chromium", "firefox", "webkit"],
      "actualProjects":  ["chromium", "firefox", "webkit"],
      "status": "covered",
      "testNames": ["hero CTA is visible and links to GitHub"] },
    ...
  ]
}
```

Consume it from CI, dashboards, or release-gating scripts.

### `COVERAGE_REPORT.md` — human-readable

The matrix table that goes into a PR. Shows green/yellow/red per cell
and an explicit Gaps list. Auto-generated; do not hand-edit.

---

## 6. Adding a new flow

Three steps:

1. **Pick a substring pattern.** If your test name is `"install button
   opens modal"`, none of the existing flow ids match — extend the
   `matchFlow` table in `coverage-suite/generate-report.ts` with a new entry.
2. **Add the cell** to `requiredMatrix` in `coverage-suite/coverage.config.ts`,
   for every site that needs it.
3. **Write the test** in `tests/<site>.spec.ts` with a name that
   matches your substring.

That's it. Re-run `bun run coverage` — your cell goes from ❌ to ✅.

---

## 7. Adding a new site

1. Add an entry to `sites[]` in `coverage-suite/coverage.config.ts`.
2. Add a `gotoLanding` URL to `fixtures/index.ts`.
3. Create `tests/<site-id>.spec.ts`.
4. Add the `requiredMatrix` rows for the flows you want to enforce.

---

## 8. CI integration

`bun run coverage:check` runs the generator and exits non-zero if
`percentCovered < 80`. The threshold is set in the Taskfile recipe.

Wire it into the pipeline **before** `task test`:

```yaml
- run: bun install
- run: bun run typecheck
- run: bun run lint
- run: bun run coverage:check   # gate: must stay above threshold
- run: bun run test
```

Lowering the threshold is a deliberate, reviewed action — it should
ship with a justification in the PR body.

---

## 9. Why not instrumented code coverage?

A real V8/Istanbul `c8`-style coverage report on the landing pages
*is* possible, but it is the wrong tool for this harness:

- The sites under test are static landing pages — the meaningful
  "coverage" is which *components* and *interactions* are exercised,
  not which lines of HTML/CSS ran.
- Code coverage on a static page that renders all components on load
  is ~100% the moment you `goto("/")`. It is not a useful signal.
- The (site × flow × browser) matrix captures what E2E coverage is
  *for*: the cross-product of "what we promise to test" against
  "what we actually exercise in CI".

If a future component grows real client-side behavior (forms, state
machines, route transitions), revisit this decision and add an
instrumented coverage pass for *that site only* — not for the
harness as a whole.

---

## 10. Summary

- **Concept:** a (site, flow) matrix, mapped to Playwright projects.
- **Source of truth:** `coverage-suite/coverage.config.ts`.
- **Scanner:** `coverage-suite/generate-report.ts` (deps: Node stdlib only).
- **Outputs:** `coverage.json` (machine), `COVERAGE_REPORT.md` (human).
- **Gate:** `bun run coverage:check` (≥ 80% covered).
- **Adding flows / sites:** edit the config, write a test, regenerate.
