# Phenotype Tools

Shared cross-repo tooling scripts (per Phenotype scripting hierarchy: `Tools/*.ps1`
for scripts >20 lines).

## `Register-StartMenuApps.ps1` — Start-Menu launcher registrar

Registers each Phenotype web app's Electrobun desktop build as a **searchable,
browsable** Windows Start-Menu shortcut that launches the app in **DEV / HMR mode**
(live hot-reload — never a frozen production bundle).

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
   - launches the latest Electrobun `launcher.exe` with `RENDERER_URL` set to the
     **live dev-server URL** → hot reload. Falls back to opening the dev URL in a
     browser if the build hasn't been produced yet.
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

### Build-completion hook

Call the registrar at the **end of each app's `electrobun build`** so a completed
build re-registers its shortcut at the latest output:

```bash
electrobun build && just register-startmenu <App>
```

For lefthook-driven repos, add a `post-build`/local hook that runs the same line.
