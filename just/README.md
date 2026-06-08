# phenotype.just — Shared just recipe libraries

Reusable `just` recipe libraries for the Phenotype monorepo. Import them from
a per-repo `justfile` to avoid duplicating the standard Rust / Go / Python
quality gates across 50+ projects.

## Files

| File | Use for |
|------|---------|
| `phenotype.just` | Rust / cargo workspace projects |
| `phenotype-go.just` | Go / module projects |
| `phenotype-python.just` | Python / uv + ruff + mypy projects |

## Conventions

- All recipes use **2-space** indentation (not tabs).
- Every recipe is preceded by a one-line `#` comment.
- Only `just` builtins — no third-party extensions.
- `ci` recipes short-circuit on the first failing gate (chained with `&&`).
- Aliases (`quality-full`) are kept where the Phenotype `task quality:full`
  target references them.

## Import pattern

Use `import?` (the optional-import form) so the parent `justfile` does not
hard-fail when a sibling check-out is missing the library.

### Example 1 — Rust repo

```just
# my-rust-tool/justfile
import? "../../phenotype-tooling/just/phenotype.just"

# Local-only recipes below; everything else comes from the library.
run:
  cargo run --bin my-tool
```

After this, `just build`, `just test`, `just ci`, `just quality-full` all
work without redeclaring them.

### Example 2 — Polyglossia repo with Go services

```just
# my-polyrepo/justfile
import? "../../phenotype-tooling/just/phenotype.just"
import? "../../phenotype-tooling/just/phenotype-go.just"

# Override an inherited recipe for a specific service.
test-go:
  go test ./services/... -count=1
```

The local `test-go` shadows the imported `test` from `phenotype-go.just`.

## Versioning

These libraries follow the parent `phenotype-tooling` repo. Bump them by
editing the file in place and committing — consumers pick up the change on
their next `git pull`. No version pinning: keep it boring.
