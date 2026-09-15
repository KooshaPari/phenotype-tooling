# devenv-abstraction

A hexagonal-architecture Go library for abstracting development environment backends (Docker, Podman, Nix, process-compose, native processes) behind a single port interface.

## Architecture

```
cmd/devenv/          CLI entry point (optional)
pkg/
  domain/            Core ports + domain types (no external deps)
    environment.go   Environment port interface + Config/Status types
    registry.go      Adapter registry (Register + New)
  adapters/
    docker/          Docker/Podman adapter (wraps docker/docker SDK)
    nix/             Nix flake / nix-shell adapter
    native/          process-compose / bare-process adapter
```

The `domain` package has zero external dependencies. Adapters import it and implement the `Environment` interface. Consumers depend only on `domain`.

## Usage

```go
import (
    "context"
    "github.com/KooshaPari/devenv-abstraction/pkg/domain"
    "github.com/KooshaPari/devenv-abstraction/pkg/adapters/docker"
)

func main() {
    reg := domain.NewRegistry()
    reg.Register(domain.BackendDocker, func() domain.Environment {
        a, err := docker.New()
        if err != nil {
            panic(err)
        }
        return a
    })

    env, err := reg.New(domain.BackendDocker)
    if err != nil {
        panic(err)
    }

    ctx := context.Background()
    if err := env.Start(ctx, domain.Config{
        Name:    "my-service",
        Backend: domain.BackendDocker,
        Image:   "golang:1.23",
        Ports:   []domain.PortMapping{{HostPort: 8080, ContainerPort: 8080, Protocol: "tcp"}},
    }); err != nil {
        panic(err)
    }
    defer env.Stop(ctx)

    result, err := env.Exec(ctx, []string{"go", "build", "./..."})
    if err != nil {
        panic(err)
    }
}
```

## Supported Backends

| Backend | Status | Notes |
|---------|--------|-------|
| `docker` | WIP (WP02) | Wraps `docker/docker` SDK v27 |
| `podman` | Planned (WP02) | Reuses docker adapter via socket |
| `nix` | WIP (WP05) | `nix develop` / `nix-shell` |
| `native` | WIP (WP04) | process-compose / bare exec |

## Development

```bash
go build ./...
go test ./...
```

## License

MIT
