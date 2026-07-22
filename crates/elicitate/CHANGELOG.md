# Changelog — elicitate

All notable changes to `elicitate` are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This crate does **not** follow semver strictly until 1.0; minor versions may include breaking changes
documented under "Changed".

## [0.2.0] — 2026-07-22

### Added
- **Async / non-blocking inbox.** `elicitate ask --async` enqueues a request
  in `~/.elicitate/inbox/` and returns immediately with `request_id` and
  `open_url`. The agent's `wait --request-id <id>` polls for the answer.
- **Inbox daemon.** `elicitate daemon` runs an HTTP server on
  `127.0.0.1:7117` serving a printable HTML form per request and an index
  page. macOS tray (`NSStatusItem`) and Windows tray (`Shell_NotifyIcon`)
  notifications appear with click-to-open deep links.
- **Install / uninstall.** `elicitate install [--prefix] [--no-launch-agent]
  [--skip-path] [--no-smoke]` copies both binaries to a stable prefix,
  optionally appends the prefix to `PATH`, and registers the daemon as a
  user service. `elicitate uninstall [--prefix] [--yes]` reverses it.
- **CLI surface expansion.** `ask --async`, `wait`, `answer`, `inbox`,
  `daemon`, `install`, `uninstall`. The new `serve` subcommand is a
  deliberate error pointing at `elicitate-mcp`.
- **Notify channels.** iMessage (Twilio SMS or Messages.app deep link) and
  email (SMTP relay) are one-way out: the user gets a link, the response
  always comes back through the browser form or CLI. Zero inbound network
  surface.
- **Installer module** (`elicitate::installer`) with platform-specific
  install paths, launch-agent / systemd / Run-key generation, and PATH
  export.
- **Views module** (`elicitate::views`) with HTML form renderer, full-page
  HTML with embedded CSS, plain-text summary, and JSON envelope.
- **Tray stubs** (compile on every platform; gated on `target_os = "macos"`
  / `"windows"` for the actual NSStatusItem / Shell_NotifyIcon).
- **13 new CLI integration tests** covering install, uninstall, async
  enqueue, inbox list, answer, and wait. **1 new MCP test** covering
  async-path tool calls. Total tests now **108 / 108 green**.

### Changed
- `bin_elicitate.rs` grew from 1 subcommand to 11. CLI now uses clap's
  `--env` feature so `--inbox-dir` can be set via `ELICITATE_INBOX_DIR`.
- `lib.rs` exposes new modules: `inbox`, `views`, `installer`. The async
  path is additive; the blocking popup API is unchanged.
- `Cargo.toml` adds `inquire` features (`date`), `clap` `env` feature,
  and `notify-rust` (optional, gated on `tray` feature for Linux notify).

### Fixed
- TTY renderer now maps `inquire::InquireError::IO` to the cancellation
  sentinel instead of erroring out, so `ask` from a closed stdin emits a
  clean `cancelled` JSON instead of stderr garbage.
- MCP `tool_router` macro now finds the registered `elicitate_mcp` tool
  by using `Self::tool_router()` instead of `Default::default()`.

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
