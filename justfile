# Phenotype-org standard justfile

default:
    @just --list

# Build workspace
build:
    cargo build --workspace

# Run tests
test:
    cargo test --workspace

# Lint (clippy + fmt --check)
lint:
    cargo clippy --workspace -- -D warnings
    cargo fmt --check

# Format code
fmt:
    cargo fmt

# Security audits (cargo-deny + cargo-audit)
audit:
    cargo deny check
    cargo audit

# Find unused dependencies
unused:
    cargo machete

# Full local CI sweep
ci: lint test audit unused

# Generate docs
docs:
    cargo doc --no-deps --workspace

# Register/refresh Windows Start-Menu shortcuts for Electrobun desktop apps.
# Each shortcut launches the app in DEV/HMR mode pointed at the live dev server.
# no-arg = all apps in Tools/apps.json; `just register-startmenu AgilePlus` = one.
# BUILD HOOK: call this at the END of each `electrobun build` step so a completed
# build always re-points its shortcut at the latest output, e.g.:
#     electrobun build && just register-startmenu {{app}}
register-startmenu app="":
    pwsh -NoProfile -File Tools/Register-StartMenuApps.ps1 {{ if app == "" { "" } else { "-App " + app } }}
