# phenotype-go-sdk

**Status:** ACTIVE
**Last updated:** 2026-06-30

## Overview

`phenotype-go-sdk` is the shared Go kernel (SSOT) for Phenotype org repos.
Active module: `packages/devhex` (devenv abstraction, hexagonal architecture).
Other packages under `packages/` are standalone (not in `go.work`) or scaffold.

## Quickstart

```bash
git clone https://github.com/KooshaPari/phenotype-go-sdk.git
cd phenotype-go-sdk
go work sync
cd packages/devhex

# Build
go build ./...

# Test (race detector required)
go test -race ./...

# Static analysis
staticcheck ./...      # install: go install honnef.co/go/tools/cmd/staticcheck@latest

# Vulnerability scan
govulncheck ./...      # install: go install golang.org/x/vuln/cmd/govulncheck@latest
```

## Conventions

- Branch naming: `chore/<req-id>-<slug>-<date>` for chore work; `feat/<req-id>-<slug>-<date>` for features
- Commit messages: Conventional Commits
- PR labels: `governance` for cleanup, `L<n>-#<n>` for tracking

## See also

- `SPEC.md` — repo specification
- `WORKLOG.md` — task audit trail (v2.1 schema)
- `llms.txt` — agent context file
- `CHANGELOG.md` — release notes
- `LICENSE-MIT` — MIT license
- `CODEOWNERS` — ownership map
- `.github/PULL_REQUEST_TEMPLATE.md` — PR checklist
- `.github/dependabot.yml` — automated dependency updates
