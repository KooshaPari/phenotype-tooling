# Phenotype-org standard justfile
#
# After 2026-06-11, this justfile is a thin shell that re-exports the shared
# `phenotype.just` library. The 9 recipes that consumers used to copy-paste
# (default, build, test, lint, fmt, audit, unused, ci, docs) are now defined
# once in `just/phenotype.just` and parameterized over the build system.
#
# Stack-specific recipes (e.g. `register-startmenu` for Electrobun desktop
# apps) stay in this file. Add new stack-specific recipes here; do not modify
# `phenotype.just` from a consumer repo.

import "just/phenotype.just"

# Register/refresh Windows Start-Menu shortcuts for Electrobun desktop apps.
# Each shortcut launches the app in DEV/HMR mode pointed at the live dev server.
# no-arg = all apps in Tools/apps.json; `just register-startmenu AgilePlus` = one.
# BUILD HOOK: call this at the END of each `electrobun build` step so a completed
# build always re-points its shortcut at the latest output, e.g.:
#     electrobun build && just register-startmenu {{app}}
register-startmenu app="":
    pwsh -NoProfile -File Tools/Register-StartMenuApps.ps1 {{ if app == "" { "" } else { "-App " + app } }}

# Measure code coverage (SSOT: see grade.sh for the canonical command)
coverage:
    #!/usr/bin/env bash
    set -euo pipefail
    if [[ -f "Cargo.toml" ]]; then
        cargo llvm-cov --workspace --fail-under-lines 85
    elif [[ -f "package.json" ]]; then
        npx jest --coverage --coverageThreshold='{"global":{"branches":85,"functions":85,"lines":85,"statements":85}}'
    elif [[ -f "pyproject.toml" || -f "setup.py" ]]; then
        pytest --cov=src --cov-report=term-missing --cov-fail-under=85
    elif [[ -f "go.mod" ]]; then
        go test -coverprofile=coverage.out -covermode=atomic ./... && go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//' | awk '{exit($1 < 85 ? 1 : 0)}'
    else
        echo "No recognized stack (Cargo.toml / package.json / pyproject.toml / go.mod) found." >&2
        exit 1
    fi
