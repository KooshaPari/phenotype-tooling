# Contributing

Thanks for your interest in the Phenotype Go SDK. This monorepo consolidates
several Go packages; contributions should follow the conventions of the package
they touch.

## Workflow

1. **Spec first** — open or update a `kitty-spec` under
   `kitty-specs/<feature>/` and get sign-off before substantial changes.
2. **Branch** — create a feature branch in a worktree:
   `git worktree add ../phenotype-go-sdk-wtrees/<topic> origin/main -b feat/<topic>`
3. **Tests** — add or update tests; PRs without tests are not merged for
   logic changes.
4. **Quality** — `just ci` (vet + build + test) must pass locally.
5. **Commit** — Conventional Commits; include package prefix where relevant
   (`feat(devhex): ...`).
6. **PR** — open against `main`; one logical change per PR.

## Per-package conventions

- **devhex** — single canonical Go module. `go work use packages/devhex`.
- **platformkit** — docs/specs only; Go code lives in `devhex`.
- **mcpkit** — deferred. See README workspace notes.

## Style

- `gofmt -s`, `goimports`.
- `go vet ./...` clean.
- `staticcheck ./...` (where configured).
- Public APIs documented with `// Package ...` / `// Func ...` comments.

## Commit hygiene

Split commits by provenance (see global `CLAUDE.md` — Dirty-Tree Commit
Discipline). Don't lump unrelated changes.

## Sign-off

By submitting a contribution, you agree to license your work under the
repository's license (see `LICENSE`).
