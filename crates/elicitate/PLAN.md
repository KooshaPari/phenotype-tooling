# elicitate — Implementation Plan

This is the working plan for bringing `elicitate` from scaffold to a tagged 0.1.0 release. It is
versioned; subsequent revisions bump `-v2.md`.

## Milestones

### M0 — Scaffold & contract (done in this revision)

- [x] Crate skeleton under `crates/elicitate/`.
- [x] `PromptSpec` / `ElicitResponse` / `FieldSpec` / `FieldValue` types with serde + schemars.
- [x] Validation function (`spec::validate`) enforcing all bounds.
- [x] Renderer dispatcher (`render::dispatch`) with platform detection.
- [x] TTY renderer (`platform/tty.rs`) using `inquire`.
- [x] macOS / Windows / Linux GUI renderers as compile-guarded skeletons.
- [x] JSON renderer (`platform/detect` `Json` mode) for deterministic CI tests.
- [x] CLI binary `elicitate` with `ask`, `validate`, `schema`, `detect`, `version`, `smoke`.
- [x] MCP server binary `elicitate-mcp` with `tools/list` + `tools/call` (single tool
      `elicitate_mcp`).
- [x] Plugins: Forgecode, Codex, Cursor with install scripts and READMEs.
- [x] Skill manifest at `.elicitate/skills/elicitate/SKILL.md`.
- [x] RESEARCH.md, SPEC.md, PRD.md, README.md, CHANGELOG.md.
- [x] Integration tests under `tests/`.
- [x] Test fixtures under `tests/fixtures/`.

### M1 — Native renderer implementation (next)

- [ ] Wire macOS renderer: `objc2` + `cocoa` build a real `NSPanel`, lay out a label + control +
      confirm/cancel, run a modal `NSApp::runModal` until the user clicks. Return the typed value
      via a captured `block` / closure stored in an `Id` trait object. (Tracked in
      `platform/macos.rs`.)
- [ ] Wire Windows renderer: `windows-sys` + `CreateWindowExW` create a top-level dialog, populate
      with `EDIT` / `COMBOBOX` / `BUTTON` controls, run `GetMessageW` in a loop, return on
      `WM_COMMAND` / `WM_CLOSE` / a `SetTimer`-driven timeout.
- [ ] Wire Linux renderer: `rfd::AsyncMessageDialog` for booleans; for richer fields, `rfd::FileDialog`
      + custom GTK4 builder; otherwise TUI.
- [ ] Add screenshot tests under `tests/render_screenshots/` (manual run only; CI skips with
      `ELICITATE_SCREENSHOTS=1`).

### M2 — Cross-client smoke

- [ ] Forgecode: register the tool, dispatch a sample prompt, screenshot the popup, and verify the
      agent loop resumes on confirm.
- [ ] Codex: write `~/.codex/mcp.toml`, run the Codex CLI with `--mcp elicitate`, and verify
      `elicitate_mcp` is callable.
- [ ] Cursor: merge `cursor-mcp.json`, restart Cursor, verify the tool list contains
      `elicitate_mcp`.

### M3 — Release

- [ ] Notarize the macOS `.app` bundle (separate `release-cut` plan).
- [ ] Sign the Windows binary with `signtool`.
- [ ] Bump version to `0.1.0`; tag the release; cut a `phenotype-tooling` release.

## PR sequencing

Each PR is small enough to review in ≤ 200 lines.

1. **PR-1:** Scaffold crate + library types + JSON schema export + unit tests. *(done in M0)*
2. **PR-2:** CLI binary + TTY renderer + integration tests. *(done in M0)*
3. **PR-3:** MCP server + JSON-RPC integration tests. *(done in M0)*
4. **PR-4:** Plugins + skill manifest. *(done in M0)*
5. **PR-5:** macOS native renderer. *(M1)*
6. **PR-6:** Windows native renderer. *(M1)*
7. **PR-7:** Linux native renderer. *(M1)*
8. **PR-8:** Cross-client smoke tests + release. *(M2 / M3)*

## Review checklist (per PR)

- [ ] `cargo fmt --all -- --check`
- [ ] `cargo clippy -p elicitate --all-targets -- -D warnings`
- [ ] `cargo test -p elicitate`
- [ ] No new outbound network deps
- [ ] Secret fields never appear in tracing output
- [ ] Public types still `Serialize + Deserialize` roundtrip cleanly

## Open questions

- **Q1.** Should the macOS renderer pin itself as an LSUIElement (no Dock icon) or run as a regular
  foreground app? — *Lean toward LSUIElement (Info.plist on the bundled `.app`); for the dev binary
  it's a no-op.*
- **Q2.** Should `elicitate-mcp` support `notifications/cancelled` so a host can dismiss an open
  prompt? — *Yes for v0.2; tracked here so we don't forget.*
- **Q3.** Should the TUI fallback print on stdout or stderr? — *Stdout, because the JSON response
  is the primary artifact. Diagnostics go to stderr.*
