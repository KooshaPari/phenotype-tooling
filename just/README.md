# `phenotype.just` — shared recipe library

## Purpose

Eliminates 31 hand-rolled `justfile` copies of the same 9-recipe
"Phenotype-org standard" boilerplate. Replaces them with a single
`import "phenotype.just"` statement.

## What it provides

| Recipe     | Purpose                                  | Stack-aware? |
|------------|------------------------------------------|--------------|
| `default`  | List all recipes                         | no           |
| `build`    | Build the workspace                      | yes          |
| `test`     | Run the test suite                       | yes          |
| `lint`     | Lint + format check                      | yes          |
| `fmt`      | Auto-format all files                    | yes          |
| `audit`    | Security audit                           | yes          |
| `unused`   | Find unused dependencies                 | yes          |
| `ci`       | Lint + typecheck + test + audit + unused | composite    |
| `docs`     | Generate docs                            | yes          |
| `dev`      | Watch mode                               | yes          |
| `clean`    | Remove build artifacts                   | yes          |
| `info`     | Print detected build system              | debug        |
| `typecheck`| Type-check                               | yes          |

## Build system detection

The library auto-detects the build system by walking up from the justfile
directory and looking for marker files:

| Marker                       | Build system |
|------------------------------|--------------|
| `Cargo.toml`                 | cargo        |
| `package.json` + `pnpm-lock.yaml` | pnpm     |
| `package.json` + `yarn.lock` | yarn         |
| `package.json` + `bun.lockb` or `bun.lock` | bun |
| `package.json` (no other lockfile) | npm  |
| `pyproject.toml` + `uv.lock` | uv           |
| `pyproject.toml` + `poetry.lock` | poetry   |
| `pyproject.toml` (no lockfile) | uv (fallback) |
| `go.mod`                     | go           |
| `mix.exs`                    | mix          |
| (none of the above)          | none — `info` recipe to debug |

## Adoption in a consumer repo

Replace the consumer's full `justfile` body with:

```just
import "phenotype.just"
```

plus any stack-specific recipes (e.g. `register-startmenu` for Electrobun
desktop apps). The shared library will auto-detect the build system.

## Cross-repo relative paths

The `import "phenotype.just"` path is **relative to the consumer's justfile
location**. Three common configurations:

| Repo layout | Path |
|-------------|------|
| `justfile` at repo root, `just/phenotype.just` in submodule | `import "phenotype.just"` (path submodule) |
| Vendored copy in-repo | `import "just/phenotype.just"` |
| Symlink to central cache | `import "/Users/.../phenotype.just"` (host-specific, not recommended) |

The recommended deployment is **git submodule** at the org level:
`just/` is a submodule of `KooshaPari/phenotype-tooling` pointing to
`KooshaPari/phenotype-just`. See `/Users/kooshapari/CodeProjects/Phenotype/repos/FLEET_100TASK_DAG_V4.md` §5 for the rollout plan.

## Versioning

SemVer. Breaking a recipe signature (e.g. changing `audit` from no-arg to
required arg) is a major bump. Adding a new recipe is minor. Fixing a bug
or improving docs is patch.

## What it does NOT do

- Does not run `migrate` / `db` recipes (stack-specific; consumer provides)
- Does not deploy / publish (consumer provides; see `pheno-deploy` roadmap)
- Does not manage containers (use `pheno-containers` or `devbox` directly)
- Does not sign releases (consumer provides; see `pheno-signing` roadmap)
