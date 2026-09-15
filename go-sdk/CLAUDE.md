# phenotype-go-sdk

SSOT for shared Go kernel packages consumed by other Phenotype repos.
Active modules: `packages/devhex` (devenv abstraction). See `go.work` for
the canonical workspace member list.

## Build & Test

All commands run from `packages/devhex` (the sole `go.work` member):

```bash
# Sync workspace
go work sync

# Build
go build ./...

# Vet
go vet ./...

# Test (with race detector — required before every push)
go test -race ./...

# Static analysis
go install honnef.co/go/tools/cmd/staticcheck@latest && staticcheck ./...

# Vulnerability scan
go install golang.org/x/vuln/cmd/govulncheck@latest && govulncheck ./...
```

## Project Layout

```
packages/
  devhex/              # devenv-abstraction module (only go.work member)
    pkg/domain/        # hexagonal ports + domain types
    pkg/adapters/      # backend adapters (docker, native, nix)
    tests/             # integration / smoke tests
  mcpkit/              # MCP binding scaffold (BUILD obligation — examples not yet landed)
  phenotype-go-auth/   # OAuth PKCE (standalone, not in go.work yet)
  phenotype-go-cli/    # Cobra wrapper (standalone)
  phenotype-go-config/ # Viper wrapper (standalone)
  phenotype-go-middleware/ # HTTP middleware stack (standalone)
  phenotype-id/        # ID/correlation generation (standalone)
go.work                # workspace root — only devhex is a member
charter.md             # scope governance — new Go modules require SOTA justification
```

## Conventions

- All tests must be table-driven where multiple cases exist.
- Run `go test -race ./...` locally before every push.
- Errors must use `fmt.Errorf("...: %w", err)` (wrapping, not formatting).
- No logic in `init()` beyond factory registration.
- New adapters must implement `domain.Environment` and register via `domain.Registry`.
- Public upstream credentials go through `resolvePublicCred()` — never literals.
- Hard rules: no `eval`, no raw error messages in responses, no `git reset --hard`.

## CI Gates (in `.github/workflows/ci.yml`)

| Job | Command | Must pass |
|-----|---------|-----------|
| `build` | `go build ./...` + `go vet ./...` + `go test -race ./...` | Yes |
| `staticcheck` | `staticcheck ./...` | Yes |
| `govulncheck` | `govulncheck ./...` | Yes |

## References

- Global baseline: `~/.claude/CLAUDE.md`
- Phenotype root: `../../CLAUDE.md`
- Scope charter: `charter.md`
- SSOT audit: `docs/sota/technical.md`
