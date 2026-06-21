# Contributing

Thanks for contributing to netweave-final2.

## Workflow

1. Branch from `main`: `git checkout -b <type>/<short-topic> origin/main`.
2. Keep commits small and scoped; preserve the existing Go backend / HTML5 Canvas frontend split.
3. Before opening a PR, run the local checks:
   - `go build ./...`
   - `go test ./...`
   - `go vet ./...`
4. Open a PR with a clear title (`<type>(scope): summary`) and reference any related issue.

## Style

- Follow `gofmt` and `go vet` defaults; don't suppress warnings.
- Keep domain logic (simulation, routing) decoupled from visualization concerns.
- New algorithms should include a brief note in the relevant `docs/` page and at least one test case.

## Reporting Issues

File issues with reproduction steps, expected vs. actual behavior, and your Go toolchain version (`go version`).
