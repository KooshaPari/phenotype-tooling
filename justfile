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
