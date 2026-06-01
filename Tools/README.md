# Phenotype Tools

Shared cross-repo tooling scripts (per Phenotype scripting hierarchy: `Tools/*.ps1`
for scripts >20 lines).

## `Register-StartMenuApps.ps1` — Start-Menu launcher registrar

Registers each Phenotype app's Electrobun desktop build as a **searchable,
browsable** Windows Start-Menu shortcut that launches the app in **DEV / HMR mode**
(live hot-reload — never a frozen production bundle).

**Native-only — no browser ever.** Every Start-Menu entry resolves to a genuine
native Electrobun `launcher.exe`
(`<electrobunBuildDir>/launcher.exe`, PE32+). There is **no browser fallback**:
if an app's `launcher.exe` is not built, the registrar **skips** that app with a
warning (`no native shell built — run electrobun build first`) instead of pointing
the shortcut at a dev URL/browser. The native `launcher.exe` itself wraps the HMR
dev server in a native window (and boots the backend where configured).

### What it does

1. Ensures the searchable Start-Menu folder
   `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Phenotype Apps\`.
2. Reads the data-driven manifest [`apps.json`](./apps.json) (one entry per app:
   name, repo, dev-server command + port, optional backend, electrobun build dir,
   `.ico`). Extensible to all ~38 apps by appending entries.
3. Per app, generates a stable launcher at
   `%LOCALAPPDATA%\PhenotypeApps\launchers\<App>-dev.cmd` that:
   - boots backend services (e.g. `cargo run -p agileplus-api`, or process-compose),
   - starts the Vite / react-router dev server **only if its port is free** (no dupes),
   - launches the latest **native** Electrobun `launcher.exe` with `RENDERER_URL`
     set to the **live dev-server URL** → hot reload. If `launcher.exe` is missing
     the launcher hard-fails with a build instruction — it never opens a browser.
4. Creates/**refreshes** a single stable-named `.lnk` (overwrites, never duplicates):
   `TargetPath = cmd.exe /c <launcher>.cmd`, `IconLocation = app.ico` (default
   fallback icon if absent), `WorkingDirectory = repo`.

### Why it's always latest-build + HMR

The launcher `.cmd` resolves `launcher.exe` under `<repo>/<electrobunBuildDir>` **at
launch time** and points the webview at the running dev server, so the window renders
the latest source with hot reload — there is no frozen `index.html` or bundled
snapshot in the target chain.

### Usage

```powershell
pwsh Tools/Register-StartMenuApps.ps1                 # all apps in apps.json
pwsh Tools/Register-StartMenuApps.ps1 -App AgilePlus  # one app
# or via just:
just register-startmenu
just register-startmenu AgilePlus
```

Idempotent and re-runnable.

### Per-build re-register hook

Because the registrar **skips any app whose `launcher.exe` does not yet exist**,
you must re-run it **after every `electrobun build`** so a freshly built native
shell gets its Start-Menu shortcut (and existing shortcuts re-point at the latest
output):

```bash
electrobun build && just register-startmenu <App>
```

- `just register-startmenu <App>` registers a single app.
- `just register-startmenu` (no arg) re-scans the whole roster, registering every
  app that now has a built `launcher.exe` and skipping the rest with a warning.

Wire this into each app repo as a `post-build` step (e.g. a lefthook local hook,
or appended to the repo's own `just build` / `electrobun build` recipe) so a
completed native build always (re)publishes its native shortcut. Until an app's
shell is built, it simply will not appear in the **Phenotype Apps** folder — by
design, there is never a browser shortcut standing in for a missing native build.
