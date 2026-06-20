# Go spike — enterprise gateway

Fork baseline: `third_party/bifrost` @ `9c0d904`

## Goal

Vendor-fork smoke test; local deltas on `feat/bifrost-local-delta` only.

## Smoke (2026-06-19)

| Command | Result | Notes |
|---------|--------|-------|
| `go build ./...` in `transports/` | **pass** (Linux CI) | UI embed stub bifrost#9; monorepo replaces bifrost#10 (MCPExternal* fields) |

## Commands

```bash
cd third_party/bifrost
go build ./...
```

See fork `docs/VENDOR_PIN.md` and `docs/LOCAL_DELTA.md`.
