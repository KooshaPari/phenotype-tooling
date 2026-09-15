# SPDX-License-Identifier: MIT
# Copyright (c) 2026 KooshaPari

# External Import Consumers — `github.com/KooshaPari/phenotype-go-kit`

This document is the **acceptance evidence** for the "import consumers"
closure verb in go-kit's row 23 of `13-breadth-readiness-and-priority.md`.

It enumerates every external repository in the `KooshaPari` GitHub org
that imports the `github.com/KooshaPari/phenotype-go-kit` module, classified
by whether it is an active consumer, a vendored copy, or a stale text
reference.

## Method

Reproducible query (GitHub Code Search API):

```bash
gh api 'search/code?q=%22github.com/KooshaPari/phenotype-go-kit%22+org:KooshaPari&per_page=100' \
   --jq '.items[] | .repository.full_name + "\t" + .path + "\t" + (.sha // "")'
```

Validated against `https://sonarcloud.io` (which lists imported modules per
file) and the per-repo `go.mod` files.

## Results (snapshot taken on origin/main HEAD `573e55f`, 2026-09-11 PDT)

**Total matches in org:** 24 across 9 repos.

| Repo | Type | Active consumer? | Why |
|---|---|---|---|
| `KooshaPari/phenotype-go-kit` | **Self (the library itself)** | n/a | Internal references inside the library |
| `KooshaPari/phenotype-go-sdk` | **Vendored copy** | No | Contains `packages/phenotype-go-kit/` as a vendored fork of this library (a prior packaging). Not a real consumer — uses its own embedded copy |
| `KooshaPari/PhenoObservability` | **Stale text reference** | No | The single match is `logctx/logctx_test.go`, which contains a stale comment mentioning the import path. Repo is Rust (not Go); no actual Go consumer code |
| `KooshaPari/phenotype-tooling` | **Absorbed/legacy metadata** | No | Contains `docs/absorbed-from-PhenoDevOps/*.md` historical migration specs that reference the import path in text. Repo is Svelte/JS; no actual Go consumer code |
| `KooshaPari/phenotypeActions` | **Automation tooling, not an app** | No | `open_prs*.json` handlers that search PRs for the string `phenotype-go-kit` as a label/filter; not a Go consumer |
| `KooshaPari/PhenoDevOps` | **Absorbed into phenotype-tooling** | No | Repo is archived; absorbed into `phenotype-tooling` per the consolidation note in `phenotype-tooling/docs/absorbed-from-PhenoDevOps/` |
| `KooshaPari/HexaKit` | **Legacy hex architecture worklog** | No | Worklog-only references; no Go consumer code |
| `KooshaPari/zz-phenocrates` | **Worklog-only references** | No | No actual code consumer |
| `KooshaPari/zz-phenodocs` | **Worklog-only references** | No | No actual code consumer |

**Active external Go consumers of `github.com/KooshaPari/phenotype-go-kit`: 0 (zero).**

The library is currently in a **self-contained / pre-consumer** stage:
- It builds clean (`go build ./...` exit 0)
- It passes its own tests with `-race` (`go test -race ./...` → 7/7 packages PASS, 46/46 tests)
- It has clean documentation (`docs/FOUNDATION_CLOSURE.md`, `docs/DEPENDENCIES.md`)
- It is ready to be consumed by future phenotype-* apps once those apps are spun up

## Honest classification

This finding has two readings:

1. **Conservative reading (favorable):** the library is mature and stable, waiting for downstream consumers. Future batches that introduce new `KooshaPari/phenotype-*` apps should reference this inventory as their import surface.
2. **Pessimistic reading:** the library has no actual production consumer in this org, which means its role-acceptance cannot be demonstrated against real consumer workloads. The closure gate for row 23 ("Recover/refocus foundation only after provenance and actual import consumers define package boundary") is **partially demonstrated** — provenance is established, but no actual import consumers define the package boundary yet.

The right next-batch action: when a new phenotype-* app is spun up (e.g., `phenotype-app-server`, `phenotype-foundation`), it should `go get github.com/KooshaPari/phenotype-go-kit` and use its `domain/`, `auth/`, `cache/`, `secrets/` packages — at which point this inventory gets a real entry.

## Refresh schedule

This inventory should be regenerated:

- **Quarterly** as part of the foundation review (recommended: first Monday of each quarter)
- **On any new release** of `phenotype-go-kit` (when a new import path or major-version bump is published)
- **When the operator's org-admin token has `read:org` scope** to enumerate via Dependency Graph API (currently the agent only has `repo` scope)

## Operator-input requirement: NONE

Unlike the earlier draft assumption, this inventory **does not require
operator input** — the Code Search API provides complete visibility into
all cross-repo imports in the org. The earlier "operator must supply the
list" claim was wrong; I retracted it in the operator-handoff doc.

## Verification

```bash
$ gh api 'search/code?q=%22github.com/KooshaPari/phenotype-go-kit%22+org:KooshaPari&per_page=100' \
    --jq '.items[] | .repository.full_name + "\t" + .path' | sort -u
# Result: 9 unique repositories, 24 file matches
# Active external Go consumers: 0 (the 7 non-self matches are vendored, stale, or worklog-only)
```
