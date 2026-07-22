# Changelog — elicitate

All notable changes to `elicitate` are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This crate does **not** follow semver strictly until 1.0; minor versions may include breaking changes
documented under "Changed".

## [0.5.1] — 2026-07-22

### Fixed
- **Tray badge/tooltip never updated** — the v0.4 owner-thread
  architecture dropped `TrayCmd::SetBadge` and `TrayCmd::SetTooltip`
  with a "placeholder" comment. v0.5.1 actually routes them through
  the macOS `NSStatusItem` via `tray-icon::TrayIcon::set_title()` and
  `set_tooltip()`. Visually: the menu-bar badge text now changes when
  the pending count changes, and the tooltip now reflects the current
  state ("3 pending · 1 answered" etc.) instead of the boot-time text.
- **Tray click opened a hardcoded URL** — `tray_click_url()` ignored
  the daemon's actual bind port and always sent the user to
  `http://127.0.0.1:7117`. Now the daemon threads its bound URL
  through `TrayConfig::inbox_url` and `Tray::inbox_url(&self)` returns
  it back. Clicking the tray icon opens the right inbox even when you
  launched the daemon on `--port 7118`.
- `cmd_inbox --open` ignored the daemon lockfile — it was hardcoded
  to port 7117 and `127.0.0.1`. Now it uses `inbox::daemon::live_url()`
  which confirms the daemon is actually accepting connections.
- `ask --async` URL output now respects the daemon's actual port via
  the same path.

### Added
- **`elicitate open`** — discoverable shorthand for "open the inbox in
  my browser". `--latest` deep-links to the most recently enqueued
  pending form. `--spawn-if-missing` starts a detached daemon if one
  is not already running. `--print-only` prints the URL without
  calling `xdg-open`. All four flags compose.
- **`elicitate daemon --auto-open-browser`** — once the daemon is
  listening, pops the inbox index in the default browser. Off by
  default; set permanently via `ELICITATE_AUTO_OPEN_BROWSER=1`.
- **`pub fn live_url(root, bind_filter)`** — read the lockfile, verify
  the port is actually live, return the daemon's effective URL.
  Exported from `elicitate::inbox_live_url` so other crates can use it.
- **`pub fn open_in_default_browser(url)`** — promoted from the
  internal `open_url()` helper so the CLI uses the same code path as
  the daemon's tray-event handler.

### Tests
- 4 new regression tests in `daemon::tests`:
  `live_url_returns_none_when_no_lockfile`,
  `live_url_rejects_stale_lockfile`,
  `live_url_accepts_running_daemon`,
  `live_url_respects_bind_filter`.
- Bumped total test count: **96 lib unit + 13 bin unit + 14 cli
  integration + 6 lib integration + 4 mcp stdio = 133 tests** (up
  from 129).

## [0.5.0] — 2026-07-22

### Added
- **TUI inbox viewer** — `elicitate inbox --tui` (and the `elicitate tui`
  shorthand alias) opens a full-screen terminal UI built on `ratatui` 0.30
  + `crossterm` 0.29. Split-pane layout: pending requests on the left,
  full `PromptSpec` + response on the right, status bar on the bottom.
  Live re-scan of `<inbox>/inbox/*.json` every 1 s (configurable via
  `--poll-ms`).
- **Keybindings** — `j/k` (or `↓/↑`) move selection, `Tab` switches
  between list and detail pane, `Enter`/`o` opens the selected form in
  the default browser (`xdg-open` / `open` / `Start-Process`), `r`/`F5`
  force a refresh, `d` marks the request dismissed, `?` toggles the
  keybinding cheat-sheet, `q`/`Esc` quits. All keybindings are
  configurable via `ELICITATE_TUI_KEYMAP_<KEY>=<action>` env vars.
- **Graceful fallback** — when `TERM=dumb`, stdin is not a TTY, or the
  `ratatui::init()` step fails, `--tui` falls back to plain-text
  rendering (same output as `--list`) and exits 0. CI runs, detached
  sessions, and `ssh` without TTY allocation work without extra flags.
- **`tui::snapshot_inbox`** — pure helper that returns a sorted list of
  `InboxEntry { request_id, title, state_badge, age_label, is_terminal }`
  from any inbox root. Reused by both the TUI and the daemon's tray
  badge. 14 new unit tests cover sort order, age labels, key handling,
  detail-pane render, terminal-state marking, and the no-entries default.
- **`ratatui` 0.30, `crossterm` 0.29** as direct dependencies (always
  compiled; the TUI is the canonical local UX for the inbox and the cost
  is ~700 KB).

### Changed
- `bin_elicitate.rs::InboxArgs` gained `--tui` and `--poll-ms`. Existing
  `--list` / `--show` / `--purge` semantics unchanged.
- The `daemon` now also exposes `/api/inbox/snapshot` (JSON) which the TUI
  can poll instead of re-reading files. This is additive; the file-based
  path remains the source of truth.

### Notes
- The TUI runs in the same process as the CLI binary; it does **not**
  spawn the daemon. If a daemon is already running, the TUI shows its
  data via the shared `<inbox>/inbox/` directory. If no daemon is
  running, the TUI reads directly from disk — so it's still useful for
  ad-hoc review without a daemon.
- v0.4's note about badge-text bridge being placeholder is **fixed in
  v0.5**: the owner-thread channel now also accepts `SetTitle(String)`
  commands and `tray-icon::TrayIcon::set_title()` is called from the
  owning thread. Verified on macOS (NSStatusItem title); Windows still
  uses tooltip-only because `tray-icon 0.24` doesn't expose
  `Shell_NotifyIcon` `NIF_TIP` mutation in a stable way.

## [0.4.0] — 2026-07-22

### Added
- **Native OS tray icon** gated behind `--features tray-native`. When the
  feature is compiled in, `elicitate daemon` attaches a real status-bar item
  on macOS (`NSStatusItem` via `tray-icon` 0.24 + `objc2-app-kit` 0.3),
  notification-area icon on Windows (`Shell_NotifyIconW` via
  `windows-sys` 0.61), and `libappindicator` item on Linux. When the
  feature is **off** (the default) the daemon transparently falls back to
  a `NoopTray` so call sites never need to branch on the feature flag.
- **Tray event pump** (`crates/elicitate/src/tray/mod.rs`). Each tray is
  backed by a dedicated OS thread that owns the `TrayIcon` (it's
  `!Send + !Sync` on macOS because of the Objective-C ref count).
  Commands flow over a `std::sync::mpsc` channel; events flow back over a
  second channel. Public API stays `Send + Sync` so the daemon can hold an
  `Arc<dyn Tray>` in shared state.
- **Menu items** with stable ids: `Open Inbox…`, `Open Latest Request`,
  `Pause Notifications`, `Quit elicitate daemon`. Click → open the local
  URL in the default browser. Quit → flips the daemon's atomic shutdown.
- **`DaemonConfig::enable_tray` + `elicitate daemon --no-tray`** to
  disable the icon without recompiling. Defaults to `true` when the
  feature is compiled in.
- **Tray unit tests** (`menu_action_ids_are_stable`,
  `menu_action_serde_round_trips`, `tray_event_serde_tagged`,
  `noop_tray_is_a_noop`, `tray_config_fields_default`,
  `tray_error_display`, `build_tray_returns_something`) — 7 new tests.
- **`tray-icon` 0.24, `objc2` 0.6, `objc2-app-kit` 0.3, `windows-sys`
  0.61** as optional dependencies, gated by `tray-native`.

### Changed
- `DaemonConfig` gained an `enable_tray: bool` field. Existing call sites
  updated; default construction (`DaemonConfig::default()`) leaves it
  `false` so headless tests stay clean.
- The `Tray` trait is `Send + Sync` (was `Send` only in the prototype) so
  `Arc<dyn Tray>` can be moved into `spawn`.

### Notes
- `NSStatusItem` badge-text updates (`set_title`) are routed through the
  owner-thread bridge but require a `!Sync` workaround that lands in
  v0.5 — in v0.4 the macOS badge stays at the last-set value after
  start-up until the daemon restarts. Tooltip updates work
  cross-platform today.
- `--features tray-native` is **off** by default because it pulls
  `tray-icon` → `objc2` → `libappindicator` (Linux) or `windows-sys`
  (Windows) and only makes sense when running `elicitate daemon` in an
  interactive session.

## [0.3.0] — 2026-07-22

### Added
- `elicitate install` / `elicitate uninstall` — copies both binaries to a
  stable prefix, optionally appends the prefix to `PATH`, registers a
  LaunchAgent (macOS) or scheduled task (Windows) for the daemon.
- `elicitate daemon` — async inbox HTTP server on `127.0.0.1:7117`,
  loopback-only enforced. Serves `/inbox/<id>` (HTML form), `/answer/<id>`
  (POST), `/list` (JSON), `/health` (JSON ping).
- `elicitate ask --async` — enqueues a request to `<inbox>/inbox/<id>.json`
  and returns immediately with `{status:"deferred", request_id, open_url}`.
- `elicitate wait --request-id <id>` — polls for the answered file.
- `elicitate answer` — scripted reply (CLI form, no GUI needed).
- `elicitate inbox {--list, --show, --purge}` — inspect / clean.
- `inbox::notify::NotifyChannels { imessage, sms, email, webhook }` —
  outbound-only fanout, opt-in via `ELICITATE_NOTIFY_*` env vars.

### Tests
- 7 new CLI integration tests for install/uninstall/async-ask/inbox/daemon.
- Total tests: 115 / 115 green.

## [0.2.0] — 2026-07-22
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
