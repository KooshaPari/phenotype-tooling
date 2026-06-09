# phenotype.just — Phenotype-org shared Rust recipe library.
# Import from a per-repo justfile via:
#   import? "path/to/phenotype.just"
# All recipes use 2-space indentation and only `just` builtins.

# Show the available recipes
default:
  @just --list

# Watch for changes (cargo-watch)
dev:
  cargo watch -x check -x test

# Build the entire cargo workspace
build:
  cargo build --workspace --all-targets

# Run all tests across the workspace
test:
  cargo test --workspace --all-targets

# Lint with clippy (warnings as errors)
lint:
  cargo clippy --workspace --all-targets -- -D warnings

# Format all crates in the workspace
fmt:
  cargo fmt --all

# Check formatting without modifying files
fmt-check:
  cargo fmt --all -- --check

# Audit crates for known security advisories
audit:
  cargo audit

# Check licenses, bans, and advisories via cargo-deny
deny:
  cargo deny check

# Detect unused dependencies (machete preferred, udeps fallback)
unused:
  cargo machete || cargo udeps

# Build rustdoc including private items, without deps
docs:
  cargo doc --workspace --no-deps --document-private-items

# Full local CI sweep — runs every gate, stops on first failure
ci:
  @just fmt-check
  @just lint
  @just test
  @just audit
  @just deny
  @just unused

# Remove the cargo build target directory
clean-target:
  cargo clean
  rm -rf target

# Alias of `ci` for parity with the workspace quality-full task
quality-full: ci

# Generate a CycloneDX SBOM at target/sbom.json
sbom:
  cargo cyclonedx --override-filename target/sbom.json
