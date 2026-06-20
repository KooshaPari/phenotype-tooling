# Go spike — CLI subscription proxy

Fork baseline: `third_party/cliproxyapi-plusplus` @ `54102578`

## Goal

Validate OpenAI-compatible `/v1/*` proxy surface; vibeproxy client absorbed per cliproxy++ `VIBEPROXY_ABSORPTION.md`.

## Smoke (2026-06-19)

| Command | Result | Notes |
|---------|--------|-------|
| `go build ./...` | **pass** | go.mod/go.sum #1031+#1032; Windows Umask guard cliproxyapi-plusplus#1033 |

## Commands

```bash
cd third_party/cliproxyapi-plusplus
go build ./...
```
