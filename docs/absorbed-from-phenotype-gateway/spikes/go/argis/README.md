# Go spike — argis plugin plane

Fork baseline: `third_party/argis-extensions` @ `0419dcf`

## Goal

Plugin/routing/SLM extensions POC before `packages/argis` absorption.

## Smoke (2026-06-18)

| Command | Result | Notes |
|---------|--------|-------|
| `go build ./...` | **pass** | graphql/gen committed in argis-extensions#82 |

## Commands

```bash
cd third_party/argis-extensions
go build ./...
```
