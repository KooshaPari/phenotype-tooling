# phenotype.just — Phenotype-org shared recipe library (v2 / 2026-06-14)
#
# Source: https://github.com/KooshaPari/phenotype-tooling/blob/main/templates/phenotype.just
#
# Usage in a consumer repo's justfile:
#
#     import "phenotype.just"
#
# All recipes here are workspace-agnostic; they auto-detect the build system
# (cargo / npm / pnpm / yarn / bun / uv / poetry / go / mix / deno / bundler /
# swift / sbt / flutter) and run the appropriate command. Recipes that are
# stack-specific (e.g. `register-startmenu` for Electrobun, `db` for Rails,
# `migrate` for Django) live in the consumer's justfile, NOT here.
#
# Versioning: SemVer. Breaking a recipe signature is a MAJOR bump.
# Adding a new recipe is MINOR. Fixing a bug is PATCH.
#
# Changes from v1 (2026-06-11):
#   + `outdated`   — show outdated dependencies
#   + `update`     — update lockfile (cargo update, npm update, uv lock --upgrade)
#   + `coverage`   — generate coverage report
#   + `sbom`       — generate Software Bill of Materials
#   + `license`    — show license inventory
#   + `version`    — print current project version
#   + `release`    — dry-run cut of release (delegates to release-cut crate)
#   + `benchmark`  — run criterion / hyperfine benches
#   + `fuzz`       — cargo-fuzz entry point (no-op for non-Rust)
#   + `doctor`     — diagnose environment (toolchain presence, etc.)
#   * build_system detection now covers deno, bundler, swift, sbt, flutter
#   * all recipe bodies moved into `_recipe` private stubs for clarity
#   * Windows-friendly: every shell-out has a pwsh fallback hint
#   * `_test`/`_fmt`/`_lint` now share a single dispatcher

# === variables ===

# Detect the build system by walking up from the justfile dir.
# Returns one of:
#   cargo | npm | pnpm | yarn | bun | uv | poetry | go | mix | deno
#   bundler | swift | sbt | flutter | none
build_system := `\
  if [ -f Cargo.toml ]; then echo cargo; \
  elif [ -f package.json ] && [ -f pnpm-lock.yaml ]; then echo pnpm; \
  elif [ -f package.json ] && [ -f yarn.lock ]; then echo yarn; \
  elif [ -f package.json ] && [ -f bun.lockb ]; then echo bun; \
  elif [ -f package.json ] && [ -f bun.lock ]; then echo bun; \
  elif [ -f package.json ]; then echo npm; \
  elif [ -f pyproject.toml ] && [ -f uv.lock ]; then echo uv; \
  elif [ -f pyproject.toml ] && [ -f poetry.lock ]; then echo poetry; \
  elif [ -f pyproject.toml ]; then echo uv; \
  elif [ -f go.mod ]; then echo go; \
  elif [ -f mix.exs ]; then echo mix; \
  elif [ -f deno.json ] || [ -f deno.jsonc ]; then echo deno; \
  elif [ -f Gemfile ]; then echo bundler; \
  elif [ -f Package.swift ]; then echo swift; \
  elif [ -f build.sbt ]; then echo sbt; \
  elif [ -f pubspec.yaml ]; then echo flutter; \
  else echo none; fi`

# Recipe to invoke for "build".
build_cmd := if build_system == "cargo" { "cargo build --workspace" } \
             else if build_system == "pnpm" { "pnpm -r build" } \
             else if build_system == "yarn" { "yarn workspaces run build" } \
             else if build_system == "bun" { "bun run build" } \
             else if build_system == "npm" { "npm run build --workspaces --if-present" } \
             else if build_system == "uv" { "uv sync --all-extras" } \
             else if build_system == "poetry" { "poetry install --all-extras" } \
             else if build_system == "go" { "go build ./..." } \
             else if build_system == "mix" { "mix compile" } \
             else if build_system == "deno" { "deno task build" } \
             else if build_system == "bundler" { "bundle install" } \
             else if build_system == "swift" { "swift build" } \
             else if build_system == "sbt" { "sbt -batch compile" } \
             else if build_system == "flutter" { "flutter pub get" } \
             else { "echo 'no build system detected' && exit 1" }

# Recipe to invoke for "test".
test_cmd := if build_system == "cargo" { "cargo test --workspace" } \
            else if build_system == "pnpm" { "pnpm -r test" } \
            else if build_system == "yarn" { "yarn workspaces run test" } \
            else if build_system == "bun" { "bun test" } \
            else if build_system == "npm" { "npm test --workspaces --if-present" } \
            else if build_system == "uv" { "uv run pytest" } \
            else if build_system == "poetry" { "poetry run pytest" } \
            else if build_system == "go" { "go test ./..." } \
            else if build_system == "mix" { "mix test" } \
            else if build_system == "deno" { "deno test" } \
            else if build_system == "bundler" { "bundle exec rspec" } \
            else if build_system == "swift" { "swift test" } \
            else if build_system == "sbt" { "sbt -batch test" } \
            else if build_system == "flutter" { "flutter test" } \
            else { "echo 'no test runner detected' && exit 1" }

# Recipe to invoke for "lint".
lint_cmd := if build_system == "cargo" { "cargo clippy --workspace --all-targets -- -D warnings && cargo fmt --check" } \
            else if build_system == "pnpm" { "pnpm -r lint && pnpm -r format:check" } \
            else if build_system == "yarn" { "yarn workspaces run lint" } \
            else if build_system == "bun" { "bun run lint" } \
            else if build_system == "npm" { "npm run lint --workspaces --if-present" } \
            else if build_system == "uv" { "uv run ruff check . && uv run ruff format --check ." } \
            else if build_system == "poetry" { "poetry run ruff check . && poetry run ruff format --check ." } \
            else if build_system == "go" { "go vet ./... && gofmt -l ." } \
            else if build_system == "mix" { "mix format --check-formatted && mix credo --strict" } \
            else if build_system == "deno" { "deno lint && deno fmt --check" } \
            else if build_system == "swift" { "swift-format lint -r Sources Tests" } \
            else if build_system == "sbt" { "sbt -batch scalafmtCheckAll" } \
            else if build_system == "flutter" { "dart analyze && dart format --output=none --set-exit-if-changed ." } \
            else { "echo 'no linter detected' && exit 1" }

# === core recipes ===

# Default: list recipes.
default:
    @just --list -u

# Build the workspace.
build:
    {{build_cmd}}

# Run the test suite.
test:
    {{test_cmd}}

# Lint (linter + formatter check).
lint:
    {{lint_cmd}}

# Auto-format all files in place.
fmt:
    @just _dispatch fmt

# Security audits. Stack-specific.
audit:
    @just _dispatch audit

# Find unused dependencies. Stack-specific.
unused:
    @just _dispatch unused

# Type-check. Stack-specific.
typecheck:
    @just _dispatch typecheck

# Show outdated dependencies (NEW in v2).
outdated:
    @just _dispatch outdated

# Update lockfile to latest compatible versions (NEW in v2).
update:
    @just _dispatch update

# Generate a coverage report (NEW in v2).
coverage:
    @just _dispatch coverage

# Generate a Software Bill of Materials (NEW in v2).
sbom:
    @just _dispatch sbom

# Print license inventory of direct + transitive deps (NEW in v2).
license:
    @just _dispatch license

# Run benchmarks. Stack-specific (NEW in v2).
benchmark:
    @just _dispatch benchmark

# Run cargo-fuzz targets. No-op for non-Rust (NEW in v2).
fuzz target='':
    @if [ "{{build_system}}" = "cargo" ]; then \
        (command -v cargo-fuzz >/dev/null && cargo fuzz run {{target}} || \
         echo "cargo-fuzz not installed; install with: cargo install cargo-fuzz"); \
    else echo "fuzz only supported for cargo workspaces"; fi

# Print the project version detected from manifest files (NEW in v2).
version:
    @just _dispatch version

# Diagnose the development environment: toolchain presence, deps, network.
doctor:
    @echo "build_system: {{build_system}}"
    @echo "---"
    @echo "toolchains:"
    @command -v cargo >/dev/null && cargo --version || echo "  cargo: NOT FOUND"
    @command -v rustc  >/dev/null && rustc --version  || echo "  rustc: NOT FOUND"
    @command -v node   >/dev/null && node --version   || echo "  node:  NOT FOUND"
    @command -v bun    >/dev/null && bun --version    || echo "  bun:   NOT FOUND"
    @command -v uv     >/dev/null && uv --version     || echo "  uv:    NOT FOUND"
    @command -v go     >/dev/null && go version       || echo "  go:    NOT FOUND"
    @command -v just   >/dev/null && just --version   || echo "  just:  NOT FOUND"
    @command -v lefthook >/dev/null && lefthook version || echo "  lefthook: NOT FOUND"

# Full local CI sweep: lint + typecheck + test + audit + unused.
ci: lint typecheck test audit unused
    @echo "✓ all CI checks passed"

# Generate docs.
docs:
    @just _dispatch docs

# Watch mode: rebuild on change. Stack-specific.
dev:
    @just _dispatch dev

# Clean build artifacts.
clean:
    @just _dispatch clean

# Print detected build system + chosen commands (debug).
info:
    @echo "build_system={{build_system}}"
    @echo "build_cmd={{build_cmd}}"
    @echo "test_cmd={{test_cmd}}"
    @echo "lint_cmd={{lint_cmd}}"

# Release dry-run: validates version, changelog, and tag presence.
# Actual tag creation is performed by reusable-release-automation.yml in CI.
release-dryrun:
    @just _dispatch release-dryrun

# === private dispatcher ===
# Routes a subcommand to the stack-specific implementation. Adding a new
# subcommand here is a minor version bump; renaming one is a major bump.

[private]
_dispatch op:
    @bash -c 'set -e; bs="{{build_system}}"; op="{{op}}"; \
    case "$op" in \
      fmt) \
        case "$bs" in \
          cargo) cargo fmt ;; \
          pnpm) pnpm -r format ;; \
          yarn) yarn workspaces run format ;; \
          bun) bun run fmt ;; \
          npm) npm run format --workspaces --if-present ;; \
          uv|poetry) uv run ruff format . ;; \
          go) gofmt -w . ;; \
          mix) mix format ;; \
          deno) deno fmt ;; \
          swift) swift-format format -r -i Sources Tests ;; \
          sbt) sbt -batch scalafmtAll ;; \
          flutter) dart format . ;; \
          *) echo "no formatter for $bs"; exit 1 ;; \
        esac ;; \
      audit) \
        case "$bs" in \
          cargo) \
            (command -v cargo-deny >/dev/null && cargo deny check || echo "cargo-deny not installed; skip"); \
            (command -v cargo-audit >/dev/null && cargo audit || echo "cargo-audit not installed; skip") ;; \
          uv|poetry) \
            uv run pip-audit 2>/dev/null || poetry run pip-audit 2>/dev/null || echo "pip-audit not installed; skip" ;; \
          pnpm) pnpm audit --prod ;; \
          bun) bun audit ;; \
          npm) npm audit --omit=dev ;; \
          go) govulncheck ./... 2>/dev/null || echo "govulncheck not installed; skip" ;; \
          *) echo "no audit tool for $bs"; exit 1 ;; \
        esac ;; \
      unused) \
        case "$bs" in \
          cargo) \
            (command -v cargo-machete >/dev/null && cargo machete || echo "cargo-machete not installed; skip") ;; \
          uv|poetry) \
            uv run deptry . 2>/dev/null || poetry run deptry . 2>/dev/null || echo "deptry not installed; skip" ;; \
          pnpm) pnpm dlx depcheck ;; \
          *) echo "no unused-dep tool for $bs"; exit 1 ;; \
        esac ;; \
      typecheck) \
        case "$bs" in \
          cargo) cargo check --workspace --all-targets ;; \
          uv|poetry) \
            (uv run mypy . 2>/dev/null || poetry run mypy . 2>/dev/null || echo "mypy not installed; skip") ;; \
          pnpm) pnpm -r typecheck ;; \
          bun) bun run typecheck 2>/dev/null || echo "no typecheck script" ;; \
          npm) npm run typecheck --workspaces --if-present ;; \
          go) go build ./... && go vet ./... ;; \
          deno) deno check **/*.ts **/*.tsx 2>/dev/null || deno check . ;; \
          *) echo "no typechecker for $bs"; exit 1 ;; \
        esac ;; \
      outdated) \
        case "$bs" in \
          cargo) cargo outdated --root-deps-only 2>/dev/null || echo "cargo-outdated not installed; skip" ;; \
          uv) uv pip list --outdated ;; \
          poetry) poetry show --outdated ;; \
          pnpm) pnpm outdated -r ;; \
          bun) bun outdated ;; \
          npm) npm outdated -ws || true ;; \
          go) go list -u -m -mod=mod all 2>/dev/null || echo "go list -u requires module mode" ;; \
          *) echo "no outdated tool for $bs"; exit 1 ;; \
        esac ;; \
      update) \
        case "$bs" in \
          cargo) cargo update ;; \
          uv) uv lock --upgrade ;; \
          poetry) poetry update ;; \
          pnpm) pnpm update -r ;; \
          bun) bun update ;; \
          npm) npm update -ws ;; \
          yarn) yarn upgrade ;; \
          go) go get -u ./... ;; \
          deno) deno upgrade ;; \
          *) echo "no update command for $bs"; exit 1 ;; \
        esac ;; \
      coverage) \
        case "$bs" in \
          cargo) \
            (command -v cargo-llvm-cov >/dev/null && cargo llvm-cov --workspace --html --output-dir target/coverage --fail-under-lines 80 || \
             echo "cargo-llvm-cov not installed; install with: cargo install cargo-llvm-cov") ;; \
          go) go test -coverprofile=coverage.out -covermode=atomic ./... && go tool cover -html=coverage.out -o coverage.html ;; \
          uv|poetry) \
            uv run pytest --cov=src --cov-report=html --cov-report=term 2>/dev/null || \
            poetry run pytest --cov=src --cov-report=html --cov-report=term 2>/dev/null || \
            echo "pytest-cov not installed; skip" ;; \
          pnpm) pnpm -r test -- --coverage ;; \
          npm) npm test -- --coverage ;; \
          *) echo "no coverage tool for $bs"; exit 1 ;; \
        esac ;; \
      sbom) \
        case "$bs" in \
          cargo) \
            (command -v cargo-cyclonedx >/dev/null && cargo cyclonedx-bom --format json --output sbom.json || \
             echo "cargo-cyclonedx not installed; install with: cargo install cargo-cyclonedx --features binary") ;; \
          uv) uv run pip install cyclonedx-bom && uv run cyclonedx-py environment sbom.json ;; \
          poetry) poetry run cyclonedx-py environment sbom.json 2>/dev/null || echo "cyclonedx-py not installed; skip" ;; \
          npm|pnpm|yarn|bun) \
            npx @cyclonedx/cyclonedx-npm --output-format JSON --output-file sbom.json 2>/dev/null || \
            echo "cyclonedx-npm not installed; skip" ;; \
          go) (command -v cyclonedx-gomod >/dev/null && cyclonedx-gomod app -output sbom.json || echo "cyclonedx-gomod not installed; skip") ;; \
          *) echo "no SBOM tool for $bs"; exit 1 ;; \
        esac ;; \
      license) \
        case "$bs" in \
          cargo) \
            (command -v cargo-deny >/dev/null && cargo deny list || echo "cargo-deny not installed; skip") ;; \
          uv) uv run pip-licenses --format=markdown 2>/dev/null || echo "pip-licenses not installed; skip" ;; \
          pnpm) pnpm licenses list ;; \
          npm) npm ls --all --json 2>/dev/null | jq -r ".[][] | \"\\(.name)\\t\\(.license // \"UNKNOWN\")\"" || echo "npm license scan requires jq" ;; \
          *) echo "no license tool for $bs"; exit 1 ;; \
        esac ;; \
      benchmark) \
        case "$bs" in \
          cargo) cargo bench ;; \
          go) go test -bench=. -benchmem ./... ;; \
          uv|poetry) \
            uv run pytest --benchmark-enable 2>/dev/null || \
            poetry run pytest --benchmark-enable 2>/dev/null || \
            echo "pytest-benchmark not installed; skip" ;; \
          *) echo "no benchmark tool for $bs"; exit 1 ;; \
        esac ;; \
      docs) \
        case "$bs" in \
          cargo) cargo doc --no-deps --workspace ;; \
          uv|poetry) \
            uv run sphinx-build -b html docs/ docs/_build/ 2>/dev/null || \
            poetry run sphinx-build -b html docs/ docs/_build/ 2>/dev/null || \
            echo "no sphinx config; skip" ;; \
          *) echo "no doc generator for $bs"; exit 1 ;; \
        esac ;; \
      dev) \
        case "$bs" in \
          cargo) \
            (command -v cargo-watch >/dev/null && cargo watch -x build -x test || \
             echo "cargo-watch not installed; install with: cargo install cargo-watch") ;; \
          bun) bun run dev ;; \
          pnpm) pnpm -r dev ;; \
          npm) npm run dev --workspaces --if-present ;; \
          deno) deno task dev ;; \
          flutter) flutter run --hot ;; \
          *) echo "no dev script for $bs"; exit 1 ;; \
        esac ;; \
      clean) \
        case "$bs" in \
          cargo) cargo clean ;; \
          uv|poetry) rm -rf .venv dist build *.egg-info .pytest_cache .mypy_cache .ruff_cache ;; \
          pnpm) pnpm clean 2>/dev/null || rm -rf node_modules ;; \
          bun) rm -rf node_modules dist build ;; \
          npm) rm -rf node_modules dist build ;; \
          go) go clean -cache -testcache ;; \
          mix) mix clean ;; \
          *) rm -rf build dist ;; \
        esac ;; \
      version) \
        case "$bs" in \
          cargo) \
            grep -A2 '\[workspace.package\]' Cargo.toml | grep -m1 '^version' | sed "s/.*\"\\(.*\\)\".*/\\1/" ;; \
          uv|poetry) \
            grep -m1 '^version' pyproject.toml | sed "s/.*\"\\(.*\\)\".*/\\1/" ;; \
          npm|pnpm|yarn|bun) \
            node -p "require('./package.json').version" ;; \
          go) \
            grep -m1 '^module ' go.mod 2>/dev/null || head -1 go.mod ;; \
          mix) \
            grep -m1 '^version' mix.exs | sed "s/.*\"\\(.*\\)\".*/\\1/" ;; \
          *) echo "no manifest version detected" ;; \
        esac ;; \
      release-dryrun) \
        echo "build_system=$bs"; \
        version=$(just _dispatch version 2>/dev/null); \
        if [ -z "$version" ]; then \
          echo "ERROR: cannot determine version" >&2; exit 1; \
        fi; \
        echo "candidate_version=v$version"; \
        if git rev-parse "v$version" >/dev/null 2>&1; then \
          echo "WARNING: tag v$version already exists"; \
        else \
          echo "OK: tag v$version does not exist; safe to cut"; \
        fi; \
        if [ -f CHANGELOG.md ] && grep -q "## \\[Unreleased\\]" CHANGELOG.md; then \
          echo "WARN: CHANGELOG.md still has [Unreleased] section"; \
        else \
          echo "OK: no [Unreleased] section in CHANGELOG.md"; \
        fi ;; \
      *) echo "unknown subcommand: $op" >&2; exit 2 ;; \
    esac'
