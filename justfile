# Phenotype-org standard justfile

default:
    @just --list

# Build workspace
build:
    cargo build --workspace --all-targets --all-features

# Check workspace without building artifacts
check:
    cargo check --workspace --all-targets --all-features

# Run tests
test:
    cargo test --workspace --all-features --all-targets

# Lint (clippy + fmt --check)
lint:
    cargo fmt --all --check
    cargo clippy --workspace --all-features --all-targets -- -D warnings

# Format code
fmt:
    cargo fmt --all

# Security audits (cargo-deny + cargo-audit)
audit:
    cargo deny check advisories
    cargo audit --deny warnings

# Find unused dependencies
unused:
    cargo machete

# Full local CI sweep
ci: check lint test audit unused

# Remove build artifacts
clean:
    cargo clean

# Generate docs
docs:
    cargo doc --no-deps --workspace --all-features

# Register/refresh Windows Start-Menu shortcuts for Electrobun desktop apps.
# Each shortcut launches the app in DEV/HMR mode pointed at the live dev server.
# no-arg = all apps in Tools/apps.json; `just register-startmenu AgilePlus` = one.
# BUILD HOOK: call this at the END of each `electrobun build` step so a completed
# build always re-points its shortcut at the latest output, e.g.:
#     electrobun build && just register-startmenu {{app}}
register-startmenu app="":
    pwsh -NoProfile -File Tools/Register-StartMenuApps.ps1 {{ if app == "" { "" } else { "-App " + app } }}
