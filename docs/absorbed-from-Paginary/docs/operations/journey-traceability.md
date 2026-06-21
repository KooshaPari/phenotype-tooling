# Journey Traceability

Implements the [phenotype-infra journey-traceability standard](https://github.com/kooshapari/phenotype-infra/blob/main/docs/governance/journey-traceability-standard.md).

A *journey* is a recorded user-facing flow: a sequence of input/output steps (text,
clicks, screenshots, OCR-ground-truth assertions) that documents how a feature is
actually used. Each journey has an associated *manifest* that pinpoints the spec
sections, design references, and acceptance criteria it covers.

## Where the implementation lives

| Component                         | Path                                                    | Status      |
|-----------------------------------|---------------------------------------------------------|-------------|
| CLI (`phenotype-journey`)         | `apps/journeys/src/content/bin/phenotype-journey/`      | implemented |
| Core lib (assertions, schema)     | `apps/journeys/src/content/crates/phenotype-journey-core/` | implemented |
| Manifest schema                   | `apps/journeys/src/content/schema/manifest.schema.json` | implemented |
| Functional requirements           | `apps/journeys/src/content/docs/FUNCTIONAL_REQUIREMENTS.md` | draft       |
| Remotion renderer                 | `apps/journeys/src/content/remotion/`                   | scaffolded  |
| VHS recording runner              | `apps/journeys/src/content/npm/playwright-record/`      | implemented |
| Viewer component (Vue 3)          | `apps/journeys/src/content/npm/journey-viewer/`         | implemented |
| Playwright driver                 | `apps/journeys/src/content/npm/journey-playwright/`      | implemented |
| **Manifests authored in this repo** | `docs/journeys/manifests/`                            | scaffolded  |

## The verify loop

`phenotype-journey` runs in two modes:

- **`mock` (default, offline)**: deterministic replay against a recorded tape.
  Runs in CI without any network. Used as the acceptance gate.
- **`live` (requires `ANTHROPIC_API_KEY`)**: drives a real browser session and
  asks an LLM to compare observed output against ground-truth assertions.
  Used for exploratory verification of new flows.

```bash
# Record a new tape (manual run, not in CI)
phenotype-journey record --tape docs/journeys/manifests/<spec-id>/tape.tape \
  --out docs/journeys/manifests/<spec-id>/

# Replay + verify (CI gate)
phenotype-journey verify --manifest docs/journeys/manifests/<spec-id>/manifest.json
```

## Status

- [x] Identify key user-facing flows (see [FUNCTIONAL_REQUIREMENTS](../../apps/journeys/src/content/docs/FUNCTIONAL_REQUIREMENTS.md))
- [x] Record VHS tapes for each flow (format = `.tape`, captured via `playwright-record`)
- [x] Author manifests in `docs/journeys/manifests/` (schema: [`manifest.schema.json`](../../apps/journeys/src/content/schema/manifest.schema.json))
- [x] Run `phenotype-journey verify` in CI (job lives in `.github/workflows/journey-verify.yml`)
- [ ] Author first 3 manifests for the spec-driven-development-engine spec
- [ ] Document the LLM-judge prompt template in `apps/journeys/src/content/docs/`

## Consumers

The same journey CLI is consumed by:

- [`hwLedger`](https://github.com/kooshapari/hwLedger) — TUI flows
- [`AgilePlus`](https://github.com/kooshapari/AgilePlus) — CLI flows
- [`thegent`](https://github.com/kooshapari/thegent) — agent session flows

Each consumer pins to the same `manifest.schema.json` version.
