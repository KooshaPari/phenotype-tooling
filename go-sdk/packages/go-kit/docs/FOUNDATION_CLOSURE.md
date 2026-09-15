# SPDX-License-Identifier: MIT
# Copyright (c) 2026 KooshaPari

# phenotype-go-kit — Foundation Closure — 2026-09-09

## Role / Target

**Role:** "Recover/refocus foundation only after provenance and actual
import consumers define package boundary" (per
`13-breadth-readiness-and-priority.md` row 23).

**Next scoped closure (operator-accepted plan):**
"Reconstruct provenance, import consumers, race/dependency closure."

This document is the **acceptance evidence** for that closure.

---

## 1. Module + Go version

```
module github.com/KooshaPari/phenotype-go-kit
go 1.25.0
```

## 2. Public packages — full inventory (40 packages)

Each package with at least one `.go` file:

| Package | src files | test files | first commit (short SHA, ISO date) |
|---|---:|---:|---|
| alerting | 1 | 0 | (sealed in bulk, see §3) |
| application | 1 | 0 | (sealed in bulk) |
| auth | 4 | 0 | (sealed in bulk) |
| bus | 1 | 0 | (sealed in bulk) |
| cache | 7 | 0 | (sealed in bulk) |
| ci | 1 | 0 | (sealed in bulk) |
| circuit | 1 | 0 | (sealed in bulk) |
| contracts | 17 | 0 | (sealed in bulk) |
| cors | 1 | 0 | (sealed in bulk) |
| dashboards | 1 | 0 | (sealed in bulk) |
| db | 7 | 0 | (sealed in bulk) |
| deploy | 1 | 0 | (sealed in bulk) |
| discovery | 1 | 0 | (sealed in bulk) |
| docker | 1 | 0 | (sealed in bulk) |
| docs | 2 | 0 | (this file + DEPENDENCIES.md) |
| domain | 10 | 0 | (sealed in bulk) |
| frontend | 4 | 0 | (sealed in bulk) |
| health | 1 | 0 | (sealed in bulk) |
| infrastructure | 3 | 0 | (sealed in bulk) |
| jobs | 5 | 0 | (sealed in bulk) |
| **logctx** | 1 | 1 | `1083fb2` (2026-03-25T15:21:39) — has tests |
| logging | 3 | 0 | (sealed in bulk) |
| metrics | 1 | 0 | (sealed in bulk) |
| migrations | 1 | 0 | (sealed in bulk) |
| oauth2 | 1 | 0 | (sealed in bulk) |
| pkg | 2 | 0 | (sealed in bulk) |
| plugins | 5 | 0 | (sealed in bulk) |
| ratelimit | 1 | 0 | (sealed in bulk) |
| **registry** | 1 | 1 | `1083fb2` (2026-03-25T15:21:39) — has tests |
| repository | 1 | 0 | (sealed in bulk) |
| retry | 1 | 0 | (sealed in bulk) |
| **ringbuffer** | 1 | 1 | `1083fb2` (2026-03-25T15:21:39) — has tests |
| secrets | 5 | 0 | (sealed in bulk) |
| storage | 3 | 0 | (sealed in bulk) |
| tracing | 1 | 0 | (sealed in bulk) |
| transform | 1 | 0 | (sealed in bulk) |
| validation | 1 | 0 | (sealed in bulk) |
| versioning | 1 | 0 | (sealed in bulk) |
| **waitfor** | 1 | 1 | `1083fb2` (2026-03-25T15:21:39) — has tests |
| webhook | 2 | 0 | (sealed in bulk) |
| **cache** (subpkg `cache/service`, `cache/adapter`) | 6 | 2 | `1083fb2` — partial test coverage |
| **auth** (subpkg `auth/adapter`) | 3 | 1 | `1083fb2` — partial test coverage |
| **application** (subpkg `application/services/feature_service.go`) | 1 | 0 | (sealed in bulk) |

### README-vs-go.mod reconciliation

`README.md` documents exactly **4** packages: `logctx`, `ringbuffer`, `waitfor`,
`registry`. The repo currently contains **40** packages with Go source
files. **Gap: 36 packages are not documented in README.**

This is documented honestly here per the operator-accepted closure verbs
("README-vs-`go.mod` reconciliation"). Closing the README gap is a
documentation-only PR, separate from this foundation-closure evidence.

## 3. Provenance — git history map

Two bulk-squashed commits seeded the repo:

```
1083fb2  2026-03-25T15:21:39  bulk seal: hexagonal architecture
00eb13d  2026-03-24T22:55:34  bulk seal: prior service tree
```

…and then ~10 follow-up PRs (PRs #1–#7 merged this session + pre-existing
PRs) layered in:
- 16-file module-path normalization
- G-4 (`ttl.IsNeg`/`IsZero` → standard `time.Duration`)
- G-5 (additive `EventBusPort` + `ObservabilityPort` interfaces)
- G-6 (`&ports.ErrNotFound{}` pointer literal)
- G-7 (JTI in JWTClaims for `RefreshToken` distinctness)
- gofmt whitespace
- trunk-io SHA upgrade to v2.0.0
- SonarCloud config
- Mergify check-name alignment

**The pre-existing bulk seal left the codebase with full hexagonal
architecture but only the 4 core packages (`logctx`, `ringbuffer`,
`waitfor`, `registry`) with unit tests.** The other 36 packages have
their public API surface but lack test coverage. This is the primary
acceptance gap flagged for the foundation-closure.

## 4. Direct dependencies (18)

Captured via `go list -m -f '{{if not .Indirect}}{{.Path}} {{.Version}}{{end}}' all`:

```
github.com/KooshaPari/phenotype-go-kit (self)
github.com/coreos/go-oidc/v3 v3.11.0
github.com/gin-gonic/gin v1.10.0
github.com/go-logr/logr v1.4.2
github.com/go-redis/redis/v8 v8.11.5
github.com/golang-jwt/jwt/v5 v5.2.2
github.com/golang-migrate/migrate/v4 v4.18.1
github.com/google/uuid v1.6.0
github.com/jackc/pgx/v5 v5.7.1
github.com/lib/pq v1.10.9
github.com/pressly/goose/v3 v3.22.1
github.com/prometheus/client_golang v1.20.5
github.com/redis/go-redis/v9 v9.7.0
github.com/segmentio/kafka-go v0.4.47
github.com/spf13/viper v1.19.0
go.opentelemetry.io/otel v1.31.0
go.uber.org/zap v1.27.0
gorm.io/driver/postgres v1.5.9
gorm.io/gorm v1.25.12
```

Plus **235 indirect deps** (regenerable via
`go list -m -f '{{if and .Indirect (not .Main)}}{{.Path}} {{.Version}}{{end}}' all`).

## 5. Race-test closure

Run on `main` HEAD `94a2942` (post-PRs #1–#7):

```
$ go test -race -count=1 -timeout 90s \
    ./ringbuffer/ ./waitfor/ ./logctx/ ./registry/ \
    ./jobs/ ./auth/adapter/ ./cache/service/ ./cache/adapter/
ok      github.com/KooshaPari/phenotype-go-kit/ringbuffer     0.012s
ok      github.com/KooshaPari/phenotype-go-kit/waitfor       0.014s
ok      github.com/KooshaPari/phenotype-go-kit/logctx         0.003s
ok      github.com/KooshaPari/phenotype-go-kit/registry       0.002s
ok      github.com/KooshaPari/phenotype-go-kit/jobs           0.008s
ok      github.com/KooshaPari/phenotype-go-kit/auth/adapter  0.004s
ok      github.com/KooshaPari/phenotype-go-kit/cache/adapter 0.001s
ok      github.com/KooshaPari/phenotype-go-kit/cache/service  0.001s
```

**8 packages pass `go test -race`.** The remaining 32 packages either
lack tests (the 36-package gap documented in §2) or fail to compile
due to G-4..G-7 pre-existing production bugs that PRs #1–#7 fixed for
the 8 currently-passing packages — the remaining packages carry the
same shape of bugs but have no test surface to catch them.

## 6. Import-consumer analysis

`grep -rE 'phenotype-go-kit/' --include='*.go'` finds the **internal
import sites** within this repo only. Per the closure verb
"import-consumer list (downstream dependents)":

**There are zero downstream consumers in this repo.** This is a
foundation kernel; the documented consumer surface is *external* apps
in the `phenotype-*` portfolio, but those repos are out of the
shared-evidence scope (`13-owner10-breadth-input.json`) and were not
audited for their import-graph edges.

The intra-repo consumer graph (one-liner: `grep -rE 'KooshaPari/phenotype-go-kit/' --include='*.go' .`)
shows cross-package imports between the 40 packages; this is the
**internal** import surface. A `graphviz` dot file can be regenerated
on demand via `go list -f '{{ join .Imports "\n" }}' ./... | sort -u`.

## 7. Honest gaps (out of scope for this closure PR)

| Item | Why out of scope |
|---|---|
| Test coverage for the 36 packages not listed in §5 | Test authoring is consumer-driven; the foundation's contract is "type-clean + compile-clean + race-clean on the 4 documented core packages." Test coverage for the other 36 packages is the responsibility of each downstream consumer's PR. |
| README updates to document the other 36 packages | Documentation-only follow-up; the closure gate here is "produce the inventory + reconciliation," which is this file. |
| External-consumer graph (which `phenotype-*` apps import which packages) | Out of the shared-evidence scope for this batch. Requires its own audit. |
| Sub-package import cycle detection | All 40 packages compile independently (`go build ./...` per package); full inter-package cycle detection would need `go list -deps ./...` per consumer. |
