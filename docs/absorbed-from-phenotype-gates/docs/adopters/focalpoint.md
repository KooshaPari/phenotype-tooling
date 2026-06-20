# FocalPoint — first adopter of `phenotype-gates`

This document records the pilot conversion of FocalPoint from hand-rolled
workflow-hygiene PRs to a single `extends: org-gates.yml` invocation. It also
links the sibling adopter repos converted in the same pilot.

## Context

FocalPoint PRs [#66][fp-66] through [#71][fp-71] were six separate, manually
maintained PRs that pinned GitHub Actions SHAs, capped workflow timeouts,
enforced `deny.toml`, and set the MSRV baseline. They were duplicated
verbatim across the org, which is exactly the "workflow-hygiene repetition"
line item on the L1-BACKLOG.

As the first adopter, FocalPoint now consumes a single shared reusable
workflow published from this repository.

## Migration

FocalPoint's `.github/workflows/ci.yml` now reduces to roughly:

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:
jobs:
  gates:
    uses: KooshaPari/phenotype-gates/.github/workflows/org-gates.yml@v0
    with:
      msrv: "1.75.0"
      gate-action-ref: "<pinned-sha-of-phenotype-gates-action>"
    secrets:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

The same shape replaces the workflow-hygiene commits previously spread
across PRs #66–#71.

## Sibling adopters in the pilot

The same `extends: org-gates.yml` swap is in flight across the rest of the
org; each link points at the corresponding migration PR:

| Repo             | Migration PR                                             |
|------------------|----------------------------------------------------------|
| FocalPoint       | #66–#71 replaced by this pilot (this document)          |
| BytePort         | [#138][bp-138]                                           |
| tooling          | [#67][tool-67]                                           |
| journeys         | [#72][jour-72]                                           |

## Acceptance checklist

- [x] `phenotype-gates/action@v0` added to FocalPoint CI
- [x] `org-gates.yml` shipped in `phenotype-org-governance` (this repo,
      under `.github/workflows/org-gates.yml`):
  - [x] workflow `timeout-minutes: 30`
  - [x] all `uses:` references pinned to action SHAs
  - [x] `deny.toml` presence enforced as a required step
  - [x] MSRV exposed as an input
- [ ] All 4 adopter repos show a single passing gate run within 24h
      *(tracked outside this repository; rolling confirmation)*
- [x] L1-BACKLOG line "workflow-hygiene repetition" marked resolved

## Operational notes

- Pinned action SHAs are recorded in `org-gates.yml` itself; bump them
  via a PR to this repo rather than in each adopter.
- The `gate-action-ref` input is the SHA of `phenotype-gates/action` (not
  a tag). Adopters MUST pin it; the gate fails closed if the input is
  missing.
- A green `gates check` is a **necessary** condition for the pilot; it
  is not sufficient to close a domain-level PR — adopters keep their
  own test/lint/typecheck jobs.

[fp-66]: https://github.com/KooshaPari/FocalPoint/pull/66
[fp-67]: https://github.com/KooshaPari/FocalPoint/pull/67
[fp-68]: https://github.com/KooshaPari/FocalPoint/pull/68
[fp-69]: https://github.com/KooshaPari/FocalPoint/pull/69
[fp-70]: https://github.com/KooshaPari/FocalPoint/pull/70
[fp-71]: https://github.com/KooshaPari/FocalPoint/pull/71
[bp-138]: https://github.com/KooshaPari/BytePort/pull/138
[tool-67]: https://github.com/KooshaPari/tooling/pull/67
[jour-72]: https://github.com/KooshaPari/journeys/pull/72
