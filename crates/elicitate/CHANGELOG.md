# Changelog — elicitate

All notable changes to `elicitate` are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This crate does **not** follow semver strictly until 1.0; minor versions may include breaking changes
documented under "Changed".

## [0.1.0] — 2026-07-21

### Added
- Initial release of the `elicitate` library, CLI, and MCP server.
- `PromptSpec` and `ElicitResponse` schemas with `serde`, `schemars`, and JSON-schema export.
- Field kinds: `boolean`, `text`, `choice`, `multiselect`, `integer`, `number`, `datetime`.
- Notes box with required/optional, max-length, default.
- Urgency: `info`, `warning`, `danger`, `secret` — used for icon and default action.
- macOS native renderer (AppKit / NSPanel, modal sheet) via `objc2` + `cocoa`.
- Windows native renderer (Win32, standard controls, password mask) via `windows-sys`.
- Linux renderer via `rfd` (GTK4 back-end); falls back to TUI when no display.
- TUI fallback (`inquire`) for headless / SSH / sandboxed environments.
- JSON renderer for `--renderer json` (CI / scripts).
- CLI: `elicitate {ask,validate,schema,detect,version,smoke}`.
- MCP server (`elicitate-mcp`): single tool `elicitate_mcp`, stdio transport, JSON-RPC 2.0.
- Plugins: Forgecode, Codex, Cursor.
- Skill: `.elicitate/skills/elicitate/SKILL.md` (universal skill manifest).
- Tracing + metrics modules (atomic counters for answered/cancelled/timed_out/failed).
- Integration tests: spec roundtrip, fixture validation, CLI smoke, MCP JSON-RPC.

### Notes
- The library is designed around the "single decision" model. If you need multi-page flows,
  build them at the caller by chaining `elicit()` calls.
- The TUI fallback is the contract. The GUI is an enhancement. CI must work without a display.

[0.1.0]: #010--2026-07-21
