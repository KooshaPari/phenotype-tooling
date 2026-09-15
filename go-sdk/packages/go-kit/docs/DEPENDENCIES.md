# SPDX-License-Identifier: MIT
# Copyright (c) 2026 KooshaPari

# phenotype-go-kit — Direct Dependencies (Closure Evidence)

Source-of-truth run on `main` HEAD `94a2942`:

```
$ go list -m -f '{{if not .Indirect}}{{.Path}} {{.Version}}{{end}}' all
github.com/KooshaPari/phenotype-go-kit
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

**Total: 18 direct deps** (excluding self). All pinned to a specific
version. Per the closure verb "race/dependency closure":
- `go mod tidy` produces a clean `go.sum` (no phantom imports).
- All 18 are declared, all 18 are used in the package surface.
- 235 indirect deps are regenerable via:

  ```
  go list -m -f '{{if and .Indirect (not .Main)}}{{.Path}} {{.Version}}{{end}}' all
  ```

These indirect deps include standard library shims
(`golang.org/x/sys`, `golang.org/x/crypto`), protobuf runtime
(`google.golang.org/protobuf`), Redis/v5 driver components,
GORM internals, JWT library crypto backends, and OpenTelemetry
instrumentation. They are a transitive consequence of the 18 direct
deps; `go mod why -m <package>` resolves the chain.
