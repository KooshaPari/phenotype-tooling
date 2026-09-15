# CLAUDE.md — devenv-abstraction

## Project Overview

- **Name**: devenv-abstraction
- **Description**: Docker-alternative VM stack with OCI/sandbox support - hexagonal architecture for container runtime abstraction across Mac, Windows, Linux
- **Location**: `/Users/kooshapari/CodeProjects/Phenotype/repos/devenv-abstraction`
- **Language Stack**: Go (1.21+), VitePress (docs)
- **Architecture**: Hexagonal (Ports & Adapters)
- **Published**: Internal (Phenotype org)

## Architecture

### Hexagonal Structure

```
internal/
├── adapters/          # Platform implementations
│   ├── mac/          # Lima/Colima + vz driver
│   ├── windows/      # WSL2 + gVisor
│   ├── linux/        # Native + gVisor
│   └── wasm/         # WASM sandbox (future)
├── domain/            # Core business logic (framework-agnostic)
├── ports/             # Interface definitions (Inbound & Outbound)
└── core/             # Application services orchestrating ports

cmd/devenv-abstraction/  # CLI entry point
pkg/oci/                 # OCI specification types
```

### Key Design Principles

1. **Ports define contracts, adapters implement them** - No adapter code in domain
2. **Dependency injection** - Core depends on interfaces, not implementations
3. **Platform detection at runtime** - Auto-detect best available runtime

## Build & Test

```bash
# Build
go build ./...

# Test
go test ./...

# Lint
golangci-lint run

# Format
go fmt ./...
```

## Documentation

Docs are in `docs/` with VitePress. GitHub Pages auto-deploys from `docs/` branch.

- **Dev**: `docs/guide/` - Getting started guides
- **Reference**: `docs/reference/` - API documentation
- **Specs**: `docs/specs/` - Architecture decision records

## Dependencies

Runtime dependencies (from `go.mod`):
- `github.com/containerd/containerd` - Container runtime
- `github.com/opencontainers/runtime-spec` - OCI spec types
- `golang.org/x/sys` - System calls (gVisor integration)
