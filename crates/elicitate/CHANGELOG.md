# Changelog — elicitate

All notable changes to `elicitate` are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This crate does **not** follow semver strictly until 1.0; minor versions may include breaking changes
documented under "Changed".

## [0.3.0] — 2026-08-08

### Added

- **`elicitate install --register-namespace <id>`** — register a daemon
  for a named inbox namespace at install time (repeatable). Each
  namespace gets its own LaunchAgent / systemd unit / scheduled task
  with a deterministic port.
- **`pub fn namespace_port(inbox_id: &str) -> u16`** — FNV-1a hash →
  `DEFAULT_PORT + offset`, range `7118..=8116`. Same id always maps to
  the same port.
- **`pub struct NamespaceAutostart { inbox_id, port, target }`** —
  surfaced in `InstallReport::namespace_autostarts` so callers can see
  what per-namespace units were written.
- **`InstallOptions::extra_inbox_ids: Vec<String>`** — list of namespace
  ids whose daemons should be registered alongside the default. Invalid
  ids become warnings, not failures.
- **`pub fn is_valid_inbox_id(id: &str) -> bool`** — validates namespace
  id shape (`[A-Za-z0-9_-]{1,64}`). Used by the installer to filter
  hostile ids.
- **`pub fn resolve_inbox_root(inbox_id: Option<&str>) -> PathBuf`** —
  maps `None`/`Some("default")` to legacy root, valid ids to
  `<parent>/inboxes/<id>`, hostile ids back to legacy root.
- **`elicitate namespace list [--json]`** — table of every registered
  namespace (inbox_id, port, daemon_live, autostart_present, pending /
  answered / expired counts, last_activity_ms).
- **`elicitate namespace show [inbox_id] [--json]`** — detail block for
  one namespace.
- **`elicitate namespace clean [--gc-age-secs N] [--inbox-id X] [--dry-run]`** —
  sweep terminal (Answered/Cancelled/Expired) entries across namespaces.
  Defaults to 7 days. Designed for cron / scheduled task automation.
- **`pub fn install_autostart_for(cli_path, inbox_id, port)`** — internal
  helper that registers a launchd plist / systemd unit / schtask for
  either the default daemon or a per-namespace daemon.

### Tests (12 new, all green)

- `parse_install_with_register_namespace` — `--register-namespace` accepts
  repeated values
- `parse_namespace_list` / `parse_namespace_show` / `parse_namespace_clean_default_age` /
  `parse_namespace_clean_with_age_and_dry_run` — CLI subcommand surface
- `namespace_port_distinct_and_deterministic` — same id → same port;
  different ids → distinct ports; never collides with `DEFAULT_PORT`
- `namespace_port_falls_in_expected_range` — every namespace port falls in
  `DEFAULT_PORT+1..=DEFAULT_PORT+999`
- `truncate_short_and_long` — table formatter correctness
- `enumerate_namespaces_default_only_when_no_units` — default row always
  present
- `is_daemon_live_returns_false_for_unused_port` — smoke check
- `gc_namespace_dry_run_keeps_files` — `--dry-run` reports without
  touching disk
- `is_valid_inbox_id_accepts_alphanumeric_dashes_underscores` — id shape
  validator
- `resolve_inbox_root_default_and_namespace` — None / "default" / valid /
  hostile all behave correctly

### Notes

- This is a **port-forward** of the v0.18.0 + v0.19.0 work from the
  `wip/2026-07-22-phenotype-tooling-absorbed-go-mod` branch against the
  current main (which has had rmcp 0.2 → 1.4, dirs 5 → 6, schemars 0.8 →
  1.2, thiserror 1.0 → 2.0 since the wip branch was created). The
  rmcp-coupled MCP router changes were dropped — they require a separate
  rmcp 1.4 API rewrite that's out of scope for this port.
- The MCP-coupled features from v0.13.0–v0.17.0 (elicitate_reply,
  elicitate_enqueue, elicitate_cancel, multi-inbox MCP routing) are not
  included in this port. They depend on rmcp 0.2 APIs and will need a
  follow-up port once the rmcp 1.4 rewrite lands.
- Version bumped 0.2.0 → 0.3.0 (minor: new features, backward-compatible
  on the CLI surface).
- Build is clean with `--no-default-features`. With `--features mcp` the
  lib fails to compile due to rmcp 1.4 API breaks in the existing
  `crates/elicitate/src/mcp/router.rs` — pre-existing, not introduced by
  this port.

### Changed

- Version bumped to 0.3.0.

## [0.9.0] — 2026-07-23

### Added
- MCP graceful shutdown via `ShutdownCoordinator`
- `elicitate-mcp --shutdown-timeout-secs N` flag (default 5s)
- `cancel_all()` drains in-flight requests on SIGINT before exit
- `#[cfg(test)]` graceful-shutdown unit tests

### Fixed
- MCP server no longer exits abruptly on stdin EOF — `select!` between `server.waiting()` and shutdown signal

## [0.8.0] — 2026-07-23

### Fixed
- `Route::Index` now serves the v0.6.0 `render_inbox_index_html()` page (was returning bare `simple_text`)
- `Route::Static` CSS now served with `Content-Type: text/css; charset=utf-8` (was `text/html`)
- `Route::Static` returns real 404 for unknown paths (was JS-style `/* not found */`)
- `write_response` accepts caller-controlled `content_type` parameter per route

## [0.7.0] — 2026-07-23

### Added
- `<form method=POST action=/inbox/{rid}/answer>` with per-field widgets:
  - `<input type=text>` for `FieldSpec::Text` (secret → `type=password`)
  - `<textarea>` for `FieldSpec::LongText`
  - `<input type=number>` for `FieldSpec::Integer`
  - `<select>` for `FieldSpec::Choice`
  - `<input type=checkbox>` for `FieldSpec::Boolean`
  - `<input type=date>` for `FieldSpec::DateTime`
  - Notes `<textarea>` when `PromptSpec.notes` is set
- `FieldValue` enum + `ElicitResponse::Answered` payload types
- `Route::Answer(rid)` handles POST → parse form-urlencoded, validate, write answer JSON, 302 redirect to `/inbox/{rid}/done`
- `Route::Done(rid)` confirmation page

### Tests
+5: form_emits_post_action, text_field_renders_input, choice_field_renders_select, boolean_field_renders_checkbox, post_handler_writes_answer

## [0.6.0] — 2026-07-23

### Added
- `views::render_inbox_index_html()` — browsable pending-requests index page with urgency badges (info / warn / urgent / secret), time-since-queued, field-kind label
- `views::render_form_html()` with navbar linking back to `/inbox`
- `views::render_answer_html()` — answer confirmation page
- Helpers: `html_escape`, `html_attr`, `format_age`, `truncate`, `unix_now_ms_diff`, `urgency_class`, `urgency_label`, `field_kind_label`

### Tests
+3: index_with_pending (question + urgency badge), form_detail_has_nav (navbar link), index_multiple_requests (warn class for Warning urgency)

## [0.5.2] — 2026-07-22

### Added
- `InboxChangeBus` — process-wide change bus broadcasting inbox mutations to all subscribers via `crossbeam-channel`
- `inbox::change::InboxWatcher` — blocking `wait_changed(timeout)` interface
- `elicitate inbox --tui --follow` — replaces 1-second wall-clock polling with ~3 ms wake-up latency
- `enqueue()` / `finalize()` call `bus::notify()` after atomic rename

### Tests
+7 change-bus concurrency unit tests

## [0.5.1] — 2026-07-22

### Fixed
- Tray badge/tooltip now actually update (owner thread was dropping `SetBadge`/`SetTooltip`)
- `tray_click_url()` no longer hardcoded to `:7117` — reads daemon's actual bound port via `TrayConfig::inbox_url`
- `elicitate inbox --open` uses `inbox_live_url` (live lockfile + TCP probe), not hardcoded port

### Added
- `elicitate open [--latest] [--spawn-if-missing] [--print-only]` — standalone open-inbox subcommand
- `elicitate daemon --auto-open-browser` — pops inbox on first bind
- `elicitate::inbox_live_url`, `elicitate::inbox_read_lockfile`, `elicitate::open_in_default_browser`

### Tests
+4: live_url_accepts_running_daemon, live_url_returns_none_when_no_lockfile, live_url_rejects_stale_lockfile, live_url_respects_bind_filter

## [0.5.0] — 2026-07-22

### Added
- Terminal inbox viewer — `elicitate inbox --tui` / `elicitate tui`
- Split-pane layout: pending requests left, full `PromptSpec` right, status bar bottom
- Live re-scan every 1s (`--poll-ms` configurable)
- Default keymap: j/k/↓↑ move, Tab switch, Enter/o open in browser, r/F5 refresh, d dismiss, ? help, q/Esc quit
- Rebindable via `ELICITATE_TUI_KEYMAP_<KEY>=<action>` env vars
- Graceful fallback: `TERM=dumb` / no TTY → plain-text output, exit 0

### Tests
+14 tui unit tests (field_summary, format_age, sort order, terminal-state marking, key handling, detail-pane render, etc.)

## [0.4.0] — 2026-07-22

### Added
- Real native tray icon behind `--features tray-native`
- Channel-based architecture: `TrayIcon` on dedicated owner thread (`objc2` types are `!Send`)
- macOS `NSStatusItem` via `tray-icon 0.24`
- Windows `Shell_NotifyIconW` via `tray-icon` + `windows-sys 0.61`
- Linux GTK backend via `tray-icon`
- Badge updates on pending-count change (clamped to u8::MAX, max display "99+")
- Click → opens `/inbox` in default browser; right-click → menu (Show / Open latest / Quiet / Quit)
- `NoopTray` fallback when feature is off or `--no-tray` is passed

### Tests
+7 tray module unit tests, +1 daemon smoke test (daemon_with_tray_disabled)

## [0.3.0] — 2026-07-22

### Added
- `elicitate install` — copies binaries, exports `PATH=`, registers LaunchAgent/schtasks
- `elicitate uninstall` — reverses idempotently
- `elicitate daemon` — local HTTP inbox server at `127.0.0.1:7117`
- `elicitate ask --async` — writes deferred request to inbox dir, agent continues immediately
- `elicitate wait --request-id ID [--timeout S]` — polls for answer
- `elicitate answer --request-id ID --value k=v` — scripted reply
- `elicitate inbox {--list, --show ID, --purge}` — inspect / clean
- Tray stubs per `cfg(target_os)` — macOS `osascript`, Windows PowerShell
- Notify fanout `NotifyChannels { imessage, sms, email }` — outbound-only, opt-in via `ELICITATE_NOTIFY_*`

### Tests
+14 CLI integration tests (install, uninstall, inbox, daemon, ask-async)

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
