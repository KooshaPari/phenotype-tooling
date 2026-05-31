# Per-App Native Desktop Stack Decisions

> Generated: 2026-05-31  
> Scope: 13 Phenotype apps  
> Excluded (do not touch): P2 / 472-P2 / KVirtualStage / KlipDot / KodeVibeGo / kwality

---

## Decision Matrix

| App | Core Tech | Recommended Desktop Stack | Rationale |
|-----|-----------|--------------------------|-----------|
| **AgilePlus** | Rust API + React/Vite web | **Electrobun** | Rich existing web UI; Rust backend boots as sidecar process |
| **Planify** | React-Router web (Plane fork) | **Electrobun** | Feature-complete web UI; wrap at zero rewrite cost |
| **OmniRoute** | Next.js web | **Electrobun** | Existing web UI; Next.js server runs as sidecar |
| **chatta** | Svelte/SvelteKit web | **Electrobun** | SvelteKit app (confirmed svelte.config.js + src/app.html); wrap directly |
| **phenoRouterMonitor** | Web dashboard | **Electrobun** | Dashboard-only; wrapping is the full story |
| **AtomsBot** | Web | **Electrobun** | Web-first; wrap |
| **AppGen** | Web | **Electrobun** | Web-first; wrap |
| **phenotype-auth-ts** | TypeScript library | **NOT a desktop app** — auth library only (hexagonal ports/adapters layout, `main` = `dist/index.js`, scripts = test/build/typecheck/docs:dev, no UI entry); ship as npm package, no desktop wrapper |
| **phenotype-org-governance** | Web | **Electrobun** | Web-first governance tooling; wrap |
| **phenodocs** | VitePress docs site | **FLAG: prefer browser** — docs belong at a URL (GH Pages / Vercel); if an offline-first reader is ever needed, Electrobun wrapping the `vitepress build` output is viable, but default = no desktop app |
| **helios-router** | Branding/tooling stub | **FLAG: not an app yet** — repo contains only `assets/brand/` and `tools/Export-Brand.ps1`; no server or UI; revisit when a router service is implemented; likely Electrobun wrapping a served page when ready |
| **HeliosLab** | Rust workspace (pheno-core / pheno-db / pheno-cli / FFI crates) | **Tauri v2** — Rust-native core with no existing web UI; Tauri lets the Rust workspace remain the backend with a thin web frontend for any GUI panels; avoids Node.js overhead for a CLI-heavy tool |
| **slickport** | SvelteKit + Drizzle/PG | **Electrobun** | SvelteKit frontend confirmed; PG backend runs as sidecar; identical pattern to chatta |

---

## Ambiguous App Resolutions

### phenotype-auth-ts — library, not an app
Repo layout is pure hexagonal (`adapters/`, `domain/`, `ports/`, `index.ts`); `package.json` exports `dist/index.js` with no web entry point. **Resolution: library only — no desktop wrapper.**

### helios-router — stub, not yet a runnable app
Repo contains brand assets and a PS1 export script with no server or UI code.  
**Resolution: flag as not-yet-an-app; apply Electrobun when a served UI exists.**

### HeliosLab — Rust workspace (no existing web shell)
Cargo workspace with `pheno-core`, `pheno-db`, `pheno-crypto`, `pheno-cli`, and FFI crates. No Electron/Tauri shell found.  
**Resolution: Tauri v2** — keeps Rust as the first-class runtime; avoids bolting Node onto a Rust project; web frontend layer (React/Svelte) added only if GUI panels are needed.

### slickport — SvelteKit web app
`svelte.config.js` + `src/app.html` confirmed. Drizzle + PG = backend sidecar pattern.  
**Resolution: Electrobun** (same as chatta).

---

## Stack Count Summary

| Stack | Apps |
|-------|------|
| Electrobun | 9 (AgilePlus, Planify, OmniRoute, chatta, phenoRouterMonitor, AtomsBot, AppGen, phenotype-org-governance, slickport) |
| Tauri v2 | 1 (HeliosLab) |
| Not a desktop app | 1 (phenotype-auth-ts) |
| Flagged / deferred | 2 (phenodocs, helios-router) |

---

## Guiding Principles: When NOT to Use Electrobun

Electrobun is the default for any app that already has a web UI. Override to a native stack only when:

| Condition | Preferred Alternative |
|-----------|-----------------------|
| Rust-native core, no existing web UI, CLI-heavy | **Tauri v2** (Rust stays first-class) |
| Deep OS integration (system tray, native menus, OS notifications, file-system drag-drop at OS level) | **Tauri v2** (smaller binary, OS APIs via Rust) |
| macOS-only, Metal/SwiftUI required | **Swift + SwiftUI** |
| Windows-only, WinUI 3 shell integration | **WinUI 3 / WinAppSDK** |
| Non-web core (2D/3D canvas, heavy compute, custom renderer) | **Slint / egui / raw wgpu** |
| Python-core app (e.g., Streamlit) | Electrobun/Tauri wrapping the served page, OR leave as a web server (no desktop wrapper mandated) |

None of the current 13 apps fall into the Swift/WinUI3/Qt/GTK/egui column — all are web-core or Rust-CLI.

---

## References

- [Electrobun](https://electrobun.dev) — Bun-powered cross-platform desktop wrapper
- [Tauri v2](https://tauri.app) — Rust-native desktop shell with optional web frontend
- Phenotype org conventions: `MEMORY/project_phenotype_org.md`
- Start Menu launchers: `MEMORY/project_start_menu_app_launchers.md`
