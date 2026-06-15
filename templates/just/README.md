# `phenotype.just` v2 — shared recipe library

## Purpose

Eliminates hand-rolled `justfile` copies of the standard 9-recipe
"Phenotype-org standard" boilerplate across 31+ consumer repos.
Replaces them with a single `import "phenotype.just"` statement.

## What it provides (v2)

| Recipe            | Purpose                                          | Stack-aware? | Since |
|-------------------|--------------------------------------------------|--------------|-------|
| `default`         | List all recipes                                 | no           | v1    |
| `build`           | Build the workspace                              | yes          | v1    |
| `test`            | Run the test suite                               | yes          | v1    |
| `lint`            | Lint + format check                              | yes          | v1    |
| `fmt`             | Auto-format all files                            | yes          | v1    |
| `audit`           | Security audit                                   | yes          | v1    |
| `unused`          | Find unused dependencies                         | yes          | v1    |
| `typecheck`       | Type-check                                       | yes          | v1    |
| `ci`              | Lint + typecheck + test + audit + unused         | composite    | v1    |
| `docs`            | Generate docs                                    | yes          | v1    |
| `dev`             | Watch mode                                       | yes          | v1    |
| `clean`           | Remove build artifacts                           | yes          | v1    |
| `info`            | Print detected build system                      | debug        | v1    |
| `outdated`        | Show outdated dependencies                       | yes          | **v2** |
| `update`          | Update lockfile to latest compatible             | yes          | **v2** |
| `coverage`        | Generate coverage report                         | yes          | **v2** |
| `sbom`            | Generate Software Bill of Materials              | yes          | **v2** |
| `license`         | Print license inventory of all deps              | yes          | **v2** |
| `version`         | Print manifest version                           | yes          | **v2** |
| `release-dryrun`  | Validate version + changelog + tag (no mutation) | composite    | **v2** |
| `benchmark`       | Run benches                                      | yes          | **v2** |
| `fuzz target`     | cargo-fuzz entry point                           | cargo only   | **v2** |
| `doctor`          | Diagnose environment toolchain presence          | debug        | **v2** |

## Build system detection (v2)

The library auto-detects the build system by walking up from the justfile
directory and looking for marker files:

| Marker                                  | Build system | Since |
|-----------------------------------------|--------------|-------|
| `Cargo.toml`                            | cargo        | v1    |
| `package.json` + `pnpm-lock.yaml`       | pnpm         | v1    |
| `package.json` + `yarn.lock`            | yarn         | v1    |
| `package.json` + `bun.lockb` / `bun.lock` | bun        | v1    |
| `package.json` (no other lockfile)      | npm          | v1    |
| `pyproject.toml` + `uv.lock`            | uv           | v1    |
| `pyproject.toml` + `poetry.lock`        | poetry       | v1    |
| `pyproject.toml` (no lockfile)          | uv (fallback)| v1    |
| `go.mod`                                | go           | v1    |
| `mix.exs`                               | mix          | v1    |
| `deno.json` / `deno.jsonc`              | deno         | **v2** |
| `Gemfile`                               | bundler      | **v2** |
| `Package.swift`                         | swift        | **v2** |
| `build.sbt`                             | sbt          | **v2** |
| `pubspec.yaml`                          | flutter      | **v2** |
| (none of the above)                     | none — use `doctor` recipe to debug | — |

## Adoption in a consumer repo

Replace the consumer's full `justfile` body with:

```just
import "phenotype.just"
```

plus any stack-specific recipes (e.g. `register-startmenu` for Electrobun
desktop apps, `migrate` for Django, `db-reset` for Rails). The shared
library will auto-detect the build system.

## Cross-repo relative paths

The `import "phenotype.just"` path is **relative to the consumer's justfile
location**. Two common configurations:

| Repo layout                                                      | Path                          |
|------------------------------------------------------------------|-------------------------------|
| `phenotype.just` is a git submodule at the consumer repo root   | `import "phenotype.just"`     |
| Vendored copy under `just/phenotype.just`                       | `import "just/phenotype.just"` |

The recommended deployment is **git submodule** at the org level. The
phenotype-tooling repo itself vendors the library under `just/` for
self-bootstrap; consumer repos should pin to a specific tag of the
submodule.

## Versioning

SemVer. Breaking a recipe signature (e.g. changing `audit` from no-arg to
required arg) is a **major** bump. Adding a new recipe is **minor**.
Fixing a bug or improving docs is **patch**.

## Migration from v1 → v2

No breaking changes. v2 is a strict superset of v1. After upgrading:

1. Bump the submodule to the `v2.0.0` tag.
2. Run `just doctor` to confirm toolchain presence.
3. Run `just outdated` once to baseline dependency age.
4. (Optional) wire `just coverage` into your CI; the threshold is
   `--fail-under-lines 80` by default — adjust the recipe if you need a
   different floor.
5. (Optional) wire `just sbom` into your release pipeline. The default
   output is `sbom.json` at the repo root; pair it with
   `reusable-release-automation.yml` for automatic attachment to GitHub
   Releases.

## What it does NOT do

- Does not run `migrate` / `db` recipes (stack-specific; consumer provides)
- Does not deploy / publish (consumer provides; see `pheno-deploy` roadmap)
- Does not manage containers (use `pheno-containers` or `devbox` directly)
- Does not sign releases (consumer provides; see `pheno-signing` roadmap)
- Does not create pull requests (consumer provides; see `pheno-pr-bot` roadmap)
