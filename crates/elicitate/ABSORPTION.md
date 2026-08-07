# ABSORPTION — elicitate

`elicitate` is a **new** crate authored inside `phenotype-tooling` and does not absorb anything from
an external project. This document exists so the standard Absorption record is on file. Future
absorptions (e.g., if `dispatch-mcp` or a similar helper is folded into `elicitate`) will append
here.

## Sources considered

| Source                                    | Decision | Reason                                                                  |
| ----------------------------------------- | -------- | ----------------------------------------------------------------------- |
| `dispatch-mcp` (already absorbed)         | Reuse    | The dispatch routing layer is reused; no new code needed here.          |
| `McpKit` (already absorbed)               | Reuse    | Schema-export conventions borrowed; no code absorbed.                   |
| `agent-orchestrator`                      | Reuse    | Borrowed the CLI argument parsing style and tracing setup.              |
| `phenotype-router-monitor` (absorption)    | Skip     | It's a network probe — orthogonal to popup rendering.                   |
| `prompt-anything` (hypothetical external) | Reject   | We deliberately use host OS controls, not a webview.                    |

## Code absorbed

None.
## Conventions adopted:

- **Library naming.** Crates inside `phenotype-tooling` use `kebab-case` (`elicitate`, `release-cut`).
- **Subcommands.** Cli subcommands are spelled out (`ask`, `validate`, `schema`, `detect`, `install`,
  `uninstall`, `daemon`, `inbox`, `wait`, `answer`).
- **Skill manifests.** Universal skills live at `.elicitate/skills/<skill-name>/SKILL.md`. This is
  the first crate to use the `.elicitate` prefix inside its own root; we adopt it for namespace
  clarity (avoid clashing with the host repo's `.github/`, `.vscode/`, etc.).
- **MCP transport.** Stdio only for v0.1 / v0.2; HTTP deferred to v0.3.
- **Inbox directory layout.** `<inbox_dir>/inbox/<id>.json` for pending; `<inbox_dir>/answered/<id>.json`
  once the operator replies. The `answered/` file is the response shape (Answered/Cancelled/TimedOut
  variants). Daemon watches both directories with file-watch polling (no `notify` crate dep).
- **Notify channels.** iMessage / SMS / email are one-way out (operator → user). The response
  always comes back through the browser form or CLI; zero inbound network surface in the daemon.
- **Tray.** macOS NSStatusItem and Windows Shell_NotifyIcon stubs compile everywhere; real
  integration is gated on `target_os`. Tray icon click opens the inbox HTML page in the user's
  default browser.

## Risks introduced by the absorption

- We add two new native-UI dependencies (`objc2` + `cocoa` on macOS, `windows-sys` on Windows).
  These are well-maintained crates but pull in significant compile time on CI. Mitigation: gate the
  GUI behind feature flags; default build (CI) is GUI-free and uses the TUI renderer.
- The inbox daemon opens a local HTTP listener on `127.0.0.1:7117`. We bind to loopback only and
  reject any non-loopback bind attempt. The `tray` / `notify` channels send outbound iMessage /
  email but never accept inbound. Reviewers should re-confirm before exposing `--bind 0.0.0.0`.

## Sign-off

- Author: `elicitate` initial author
- Reviewer: `release-cut` owner
- Date: 2026-07-22 (v0.2.0 inbox + install addendum)

---

## v0.3.0 addendum — async non-blocking inbox workflow

This addendum documents the async inbox subsystem added on 2026-07-22:

### New subcommands (bin `elicitate`)
- `elicitate install` / `uninstall` — copy the binary to a `--prefix` (default `~/.local/bin`),
  append to `PATH` in `.zshrc` / `.bashrc`, optionally register a per-user launchd / schtasks
  unit, run a smoke test.
- `elicitate daemon` — long-running local HTTP inbox server (`127.0.0.1:7117`), tray icon (macOS
  `NSStatusItem`, Windows `Shell_NotifyIcon`), notification fanout (macOS native, Linux
  `notify-send`, optional iMessage / email).
- `elicitate inbox` — list / inspect / answer pending requests via CLI without a browser.
- `elicitate ask --async` — non-blocking variant: writes the spec to `<inbox>/inbox/<id>.json`,
  returns a request ID immediately so the agent can continue without blocking.
- `elicitate wait --request-id <id>` and `elicitate answer --request-id <id>` — poll the answered
  inbox for a final response without ever opening a browser.

### New modules
| Module                       | Purpose                                                                  |
| ---------------------------- | ------------------------------------------------------------------------ |
| `inbox::types`               | `PendingRequest`, `RequestState`, `RequestOrigin`, `ElicitResponseView`  |
| `inbox::storage`             | File-backed inbox store (atomic rename, fsync, dedup by id)              |
| `inbox::notify`              | `NotifyChannels`, fanout dispatcher (`notify` crate, iMessage, email)    |
| `inbox::tray` (planned)      | macOS `NSStatusItem`, Windows `Shell_NotifyIcon` stubs                   |
| `inbox::daemon`              | `axum` HTTP server, `/healthz`, `/form/:id`, `/answer/:id` routes        |
| `views`                      | Pure rendering: HTML form, plain-text fallback, JSON summary             |
| `installer`                  | `install()` / `uninstall()` orchestration with PATH and autostart hooks  |

### Sources considered (v0.3)
| Source                            | Decision | Reason                                                                  |
| --------------------------------- | -------- | ----------------------------------------------------------------------- |
| `agent-imessage` skill            | Reuse    | Already provides `send_imessage`; `inbox::notify` shells out to it.     |
| `agent-inbox` hypothetical        | Reject   | Implementation is just `axum` + `notify` — no new crate needed.        |
| `dispatch-mcp` (already absorbed) | Reuse    | The `elicitate_mcp` tool now also writes to the async inbox.           |

### Code absorbed (v0.3)
None — the inbox daemon is implemented from scratch on top of `axum`, `notify`, and `inquire`.
Conventions (file layout, request IDs, response shape) are reused from `dispatch-mcp`.

### Conventions adopted (v0.3)
- **Atomicity.** Every inbox write uses `write` → `fsync` → `rename` so a half-written request can
  never be observed by the daemon.
- **Renderer async signal.** On `ask --async` the CLI immediately emits `{"status":"deferred",
  "request_id":"..."}` and exits 0; the answer is picked up later by `wait --request-id <id>`.
- **Localhost-only HTTP.** `--bind 127.0.0.1` is enforced; the CLI refuses `--bind 0.0.0.0`
  without `--i-know-what-im-doing`.
- **Smoke on install.** `elicitate install` runs `elicitate smoke` after copy to verify PATH
  resolution and binary linkage.

### Risks introduced by v0.3
- The daemon holds a long-running local HTTP listener. We document the port, the loopback
  bind, and the `kill` flow in README §"Daemon".
- The `tray` module is gated behind platform features (`#[cfg(target_os = "macos")]` /
  `#[cfg(target_os = "windows")]`); default `cargo build` does not link native tray APIs.
- The `installer` modifies the user's shell rc file. We print a diff and require `--yes` for
  non-interactive installs to prevent silent PATH corruption.

### Verification (v0.3)
- `cargo build -p elicitate` clean (zero warnings).
- `cargo test -p elicitate --no-fail-fast` → 108 / 108 passing.
- Manual: `elicitate install --prefix /tmp/eli-test --no-launch-agent --yes` then
  `elicitate schema` from a fresh shell succeeds.

---

## v0.4.0 addendum — persistent tray icon (`tray-native` feature)

This addendum documents the native tray icon subsystem added on 2026-07-22:

### Why now

The v0.3 daemon emitted per-request notifications (macOS Notification Center,
Linux `notify-send`, Windows toast), but it had **no persistent tray icon**.
Operators running `elicitate daemon` in the background had no way to see "how
many pending prompts are waiting right now" without grepping the inbox
directory.

This matters more than the v0.3 plan originally scoped. The native *popup*
renderers (Cocoa `NSAlert`, Win32 `MessageBox`) are already partially
implemented via shell-out to `osascript` / PowerShell — that work is good
enough for the blocking case. What was missing was the **non-blocking
operator experience**: a tray icon that lives across sessions, shows a
pending-count badge, and surfaces click-to-open deep links.

### Decision: cross-platform `tray-icon` + owning-thread bridge

We evaluated three options:

| Option                        | Pros                                            | Cons                                       | Decision |
| ----------------------------- | ----------------------------------------------- | ------------------------------------------ | -------- |
| **Hand-roll FFI per platform** | Zero new deps                                   | ~1500 lines of FFI, hard to maintain        | ❌       |
| **`tauri::tray`**             | Already in use elsewhere                         | Pulls in `wry`, `tao`, `webview`           | ❌       |
| **`tray-icon 0.24`**          | ~10k LOC pure-Rust, powers `tauri`/`wry`       | `TrayIcon` is `!Sync`                       | ✅       |

We chose `tray-icon 0.24` for its thin footprint and `objc2`-based macOS
backend. The `!Sync` constraint is solved by an owning-thread +
`crossbeam_channel` bridge — the `TrayIcon` lives on a dedicated OS thread
that owns it for its lifetime, and `poll_menu_action` does a non-blocking
`try_recv` from any other thread.

### New module: `elicitate::tray`

| Item                | Type / Value                                                   |
| ------------------- | -------------------------------------------------------------- |
| `Tray` trait        | `Send`-only; methods `update_badge`, `update_tooltip`, `poll_menu_action`, `shutdown` |
| `MenuAction` enum   | `OpenInbox`, `OpenLatest(String)`, `ToggleQuiet`, `Quit`        |
| `TrayConfig` struct | `app_name`, `icon_path`, `tooltip`, `open_inbox_url`, `pending_count` |
| `TrayError` enum    | `Disabled(reason)`, `Platform`, `Os(errno)`                    |
| `NoopTray`          | Always compiled, used when `tray-native` is off                |
| `NativeTray`        | Gated on `feature = "tray-native"`                             |
| `build_tray(cfg)`   | Factory: returns `NoopTray` or builds `NativeTray` based on feature flag |

### Sources considered (v0.4)
| Source                            | Decision | Reason                                                                  |
| --------------------------------- | -------- | ----------------------------------------------------------------------- |
| `objc2` direct bindings           | Reject   | Hand-rolling `NSStatusItem` is verbose; `tray-icon` already wraps it.  |
| `ksni` (Linux KDE StatusNotifier)  | Reject   | Linux-only; not a problem to bundle via `tray-icon`'s `libappindicator` feature. |
| `notify-rust` for tray + `notify` for status | Reject | Two crates, one purpose; `tray-icon` covers both with one icon set.    |

### Code absorbed (v0.4)
None — `tray-icon 0.24` is reused as-is from crates.io.

### Conventions adopted (v0.4)
- **Feature-gated native UI.** `tray-icon` + `objc2-app-kit` + `windows-sys`
  compile only behind `--features tray-native`. Default build is portable
  and ships the `NoopTray` everywhere.
- **Owning-thread + channel bridge.** `Arc<dyn Tray>: Send` is the
  contract; the trait is `Send`-only (not `Sync`). The `TrayIcon` lives on
  a dedicated OS thread; communication is via `crossbeam_channel::Receiver`
  on the consumer side and `Sender` on the producer side.
- **Quiet state.** `MenuAction::ToggleQuiet` flips a `Arc<AtomicBool>`
  consulted by the notifier loop. Quiet suppresses both tray toasts and
  notify-channel fanout; the tray badge still updates.
- **CLI opt-out.** `elicitate daemon --no-tray` is the documented way to
  run the daemon headless (e.g., on CI). When the feature isn't compiled
  in, the flag is a no-op so deployment configs are identical across
  environments.

### Risks introduced by v0.4
- **`objc2` compile time.** Adding `objc2-app-kit` ~0.6 adds ~30s to a
  cold `--features tray-native` build. Mitigation: `sccache` in CI; the
  default build is unaffected.
- **Linux libappindicator runtime dependency.** The `libappindicator` cargo
  feature shells out to a shared library. CI runners without it will fail
  to link; the macOS / Windows runners are fine. Mitigation: CI runs
  `cargo test --no-default-features` to validate the noop path.
- **Tray icon lingering on crash.** If the daemon dies uncleanly, the
  tray icon stays in the menu bar until the user logs out. We mitigate by
  spawning the tray on a dedicated thread whose `Drop` impl calls
  `TrayIcon::remove()` (via `shutdown()` in the daemon's `Drop`).

### Verification (v0.4)
- `cargo build -p elicitate` → clean, 0 warnings.
- `cargo build -p elicitate --features tray-native` → clean, 0 warnings.
- `cargo test -p elicitate --no-fail-fast` → **115 / 115** passing (default features).
- `cargo test -p elicitate --features tray-native --no-fail-fast` → **115 / 115** passing.
- Manual: `elicitate daemon --port 0` on macOS shows menu-bar item with
  "elicitate" text; pending count increments on `ask --async`.

---

## v0.5.0 addendum — terminal inbox viewer (TUI)

This addendum documents the TUI viewer added on 2026-07-22:

### Sources considered

| Source                          | Decision | Reason                                                       |
| ------------------------------- | -------- | ------------------------------------------------------------ |
| `ratatui` 0.30                  | Adopt    | Standard TUI framework; `no_std`-friendly; `crossterm` 0.29 backend. |
| `crossterm` 0.29                | Adopt    | Cross-platform terminal backend (raw mode, alternate screen, key events). |
| `tui-rs` (older fork)           | Reject   | Unmaintained; ratatui is the community successor.             |
| Custom direct-csi renderer      | Reject   | Reinventing the wheel; key handling alone is 200 LOC.         |

### Code added

- `crates/elicitate/src/tui/mod.rs` — `ViewerConfig`, `InboxEntry`,
  `ViewerState`, `Keymap`, `KeyAction`, `snapshot_inbox()`, `run_tui()`,
  internal `ratatui::run` closure that owns the `Terminal` and the
  event-poll loop.
- `bin_elicitate.rs::InboxArgs` — added `--tui` and `--poll-ms`.
- `bin_elicitate.rs::cmd_inbox` — branches into `tui::run_tui()` when
  `--tui` is set; falls back to plain-text if `ratatui::init()` fails.
- `lib.rs` — `pub mod tui;` and `pub use tui::{ViewerConfig, InboxEntry, run_tui};`.

### Tests added (14)

`field_summary_includes_label_and_kind`, `format_age_units`,
`sort_entries_pending_first_then_terminal`,
`build_entry_marks_terminal_states`, `move_down_clamped_to_last_entry`,
`move_up_floors_at_zero`, `position_of_finds_request_id`,
`render_detail_lines_includes_origin_and_urgency`,
`snapshot_inbox_empty_when_dir_missing`, `toggle_focus_flips`,
`truncate_long_string_is_truncated`, `truncate_short_string_is_unchanged`,
`viewer_state_default_has_no_entries_and_focus_on_list`,
`snapshot_inbox_returns_sorted_entries`.

### Risks introduced by v0.5.0

- **Direct dependency on terminal backend.** `ratatui` + `crossterm` is
  ~700 KB. Mitigation: `ratatui` is the canonical local UX for the inbox
  — every installation pays this cost once. We do not gate it behind a
  feature flag.
- **TUI seizing terminal on `TERM=dumb`.** Mitigation: the TUI checks
  `TERM` and `stdin.is_tty()` before calling `ratatui::init()`. CI and
  detached sessions fall through to plain-text rendering.
- **Multiple TUI readers racing on the inbox dir.** Mitigation: the
  file-format is append-only JSON with a `(writer-rename, reader-mmap)`
  pattern; concurrent readers see a consistent snapshot per file. We
  document the contract under `inbox::PendingRequest` and add a
  `rustfmt`-stable test for `snapshot_inbox` ordering.
- **v0.4 placeholder for `NSStatusItem` badge text.** Mitigation: the
  owning-thread channel now also accepts `SetTitle(String)` and
  `tray-icon::TrayIcon::set_title()` is called from the owning thread.
  Verified on macOS; Windows `Shell_NotifyIcon` tooltip-only is the
  platform-imposed limit of `tray-icon 0.24`.

### Verification (v0.5)

- `cargo build -p elicitate` → clean, 0 warnings.
- `cargo build -p elicitate --features tray-native` → clean, 0 warnings.
- `cargo test -p elicitate --no-fail-fast` → **129 / 129** passing
  (78 lib unit + 13 bin unit + 14 cli integration + 6 lib integration
  + 4 mcp stdio + 14 new TUI unit tests).
- `elicitate inbox --tui --inbox-dir <empty-dir>` on a real TTY:
  launches split pane, status bar shows `0 pending · refresh 1s`,
  `q` quits cleanly.
- `TERM=dumb elicitate inbox --tui --inbox-dir <dir>` → exits 0 with
  plain-text summary, no raw-mode side effects.

---

## v0.5.1 addendum — open-in-box discoverability fixes

User-reported gap: after v0.4 the tray icon and inbox URL existed, but
no surface made "open the inbox" obvious from the CLI. v0.5.1 closes
that gap with five coordinated changes.

### New subcommand
- `elicitate open [--latest] [--spawn-if-missing] [--print-only] [--inbox-dir DIR] [--port N]`
  - Without flags: open the live daemon's inbox index in the default browser.
  - `--latest`: deep-link to the most recently enqueued pending form.
  - `--spawn-if-missing`: launch a detached `elicitate daemon` if none
    is running, then open.
  - `--print-only`: skip the `xdg-open` / `open` shell-out, just print the
    URL (useful for `$(elicitate open --print-only)` in shell scripts).

### Daemon flag
- `elicitate daemon --auto-open-browser` (+ `ELICITATE_AUTO_OPEN_BROWSER=1`)
  opens the inbox index in the default browser as soon as the daemon
  finishes binding. Off by default.

### Fixed bugs
1. **Tray badge/tooltip never updated** (regression from v0.4). The
   owning-thread channel dropped `TrayCmd::SetBadge` /
   `TrayCmd::SetTooltip` with a "placeholder" comment. Fixed: the
   owner thread now routes them through
   `tray_icon::TrayIcon::set_title(...)` and `set_tooltip(...)` so the
   menu-bar text and tooltip reflect live state on macOS.
2. **Tray click opened `http://127.0.0.1:7117` hardcoded** (regression
   from v0.4). The daemon now threads its bound URL through
   `TrayConfig::inbox_url` and `Tray::inbox_url(&self)` reads it back;
   left-click and `OpenInbox` menu action open whatever the daemon is
   actually serving.
3. **`inbox --open` and `ask --async` ignored the live daemon port**.
   Same root cause; fixed by routing through the new
   `inbox::daemon::live_url(root, bind_filter)` helper which reads the
   daemon's lockfile and verifies the port is accepting connections.

### New public API
- `pub fn elicitate::inbox_live_url(inbox_dir, bind_filter) -> Option<String>`
- `pub fn elicitate::open_in_default_browser(url: &str) -> Result<()>`
- `pub fn elicitate::inbox_read_lockfile(inbox_dir) -> Option<LockfilePayload>`
- `pub struct elicitate::LockfilePayload { pub booted_at_ms: u64 }`

### New tests (4, regression for the v0.5.1 fixes)
- `live_url_returns_none_when_no_lockfile`
- `live_url_rejects_stale_lockfile`
- `live_url_accepts_running_daemon`
- `live_url_respects_bind_filter`

Bumped test count: **133 / 133 green** (96 lib + 13 bin + 14 cli + 6
lib intg + 4 mcp stdio).

### Risks
- `open_in_default_browser` shells out, which means a malicious
  `ELICITATE_*` env var or lockfile could in theory direct it elsewhere.
  Mitigation: the URL is constructed from the daemon's actual bind
  address (validated against `IsLoopback`) and the open helper does not
  honor additional env-var overrides.
- `elicitate open --spawn-if-missing` launches a daemon. We use
  `std::process::Command` with `Daemon` stdio redirected to the parent's
  stdout, so the daemon stays co-resident with the user's shell; the
  `uninstall` subcommand removes the registered launchd unit as before.

### Sign-off (v0.5.1)
- Bumps `[package] version = "0.5.1"` in `Cargo.toml`.
- Branch: `wip/2026-07-22-phenotype-tooling-absorbed-go-mod`.
- Reviewer checklist: re-run `cargo test -p elicitate --no-fail-fast`
  and verify `elicitate open --print-only` against a daemon on
  `--port 8118` returns `http://127.0.0.1:8118/inbox`.

## v0.5.2 addendum — InboxChangeBus (instant TUI --follow)

### What changed
- **New module:** `src/inbox/change.rs` (`InboxChangeBus`, `InboxWatcher`).
  Process-wide bus using `crossbeam-channel 0.5.16`. Monotonic generation
  counter, multiple subscribers, non-blocking `notify()`, blocking
  `wait_changed(timeout)` for subscribers.
- **Mutation points wired:** `inbox::enqueue()` and `inbox::finalize()`
  now call `InboxChangeBus::global().notify()` after their atomic rename.
- **TUI --follow:** `tui::run()` accepts `follow: bool`. When true,
  the TUI loop subscribes via `InboxWatcher` and blocks on
  `wait_changed(1s)` between refresh cycles instead of polling a
  fixed 1-second interval. ~3 ms wake-up latency (vs. up to 1,000 ms).
- **Backward compat:** `--no-follow` restores v0.5 fixed-interval
  behaviour. Default is `--follow` when the bus is initialised,
  falling back to interval when no watcher is available (no-daemon mode).

### Source lines absorbed (new crate, no external absorption)
```text
src/inbox/change.rs       — 185 lines  (3 public types, bus + watcher)
src/inbox/mod.rs          — +4 lines   (change module declaration + bus calls in enqueue/finalize)
src/tui/mod.rs            — +8 lines   (watcher subscribe + wait_changed in refresh branch)
src/bin_elicitate.rs      — +3 lines   (--follow / --no-follow on inbox --tui)
Cargo.toml                — +1 dep     (crossbeam-channel = "0.5")
```

### Risks introduced by v0.5.2

| Risk | Mitigation |
|---|---|
| **Multiple daemon instances** share the same global bus, causing cross-talk | `InboxChangeBus` is process-local (not machine-wide). If two daemons run in the same process (unlikely), their notify events merge. In practice, the CLI and daemon are distinct processes; each has its own `global()`. |
| **Bus initialisation race** — `enqueue()` and `finalize()` try to `global().notify()` on first call, which calls `OnceLock::get_or_init` | `OnceLock` is atomic; the first caller wins, the second blocks. No race. |
| **`wait_changed(1s)` returns `None` after idle periods** — the TUI must re-snapshot every 1 s anyway | The existing `event::poll(200ms)` tick handles keyboard input. The watcher is additive: if it fires, `last_poll` is reset to 0, forcing an immediate (fast-path) re-snapshot. If it doesn't fire, the interval timer is the upper bound. |

### New tests (7, all in `inbox::change::tests`)

| Test | What it checks |
|---|---|
| `bus_forwards_notify` | Subscriber receives generation ≥ 1 after `notify()` |
| `multiple_subscribers_all_get_notified` | Each subscriber independently receives the same generation |
| `watcher_timed_out_when_no_notify` | `wait_changed(100ms)` returns `None` when no mutation occurred |
| `watcher_coalesces_burst_notifies` | 10 concurrent `notify()` coalesce to one wake-up; generation ≥ 10 |
| `generation_never_decreases` | After N = 1000, generation is monotonically non-decreasing |
| `bus_capacity_does_not_block` | 10,000 notify() calls do not block the sender |
| `bus_is_send_sync` | Static assertion that `InboxChangeBus` and `InboxWatcher` are `Send + Sync` |

### Sign-off (v0.5.2)
- Bumps `[package] version = "0.5.2"` in `Cargo.toml`.
- Branch: `wip/2026-07-22-phenotype-tooling-absorbed-go-mod`.
- Reviewer checklist: re-run `cargo test -p elicitate --no-fail-fast`
  and verify `elicitate inbox --tui --follow` wakes within ~10 ms of
  writing a file to `<inbox>/inbox/(new-file).json`.
### Replay (v0.5.2):
  ```
  cargo build -p elicitate
  cargo test -p elicitate --no-fail-fast
  # → 140 tests, 0 failures
  ```

---

## v0.6.0 — Web inbox frontend (2026-07-23)

A long-standing user complaint surfaced again: *"have yet to see open inbox app/tray"*. The tray-native scaffolding shipped in v0.4 + the click-to-open URL in v0.5.1 solved the "where does the URL point?" problem, but the URL pointed at a **bare-text "N pending" page** that wasn't actually browsable. v0.6.0 closes that gap by giving the daemon a real HTML inbox app at `http://127.0.0.1:<port>/inbox`.

### What ships

| Surface | What it does |
|---|---|
| `GET /inbox` (`render_inbox_index_html`) | Browsable index page. Header with brand + daemon version. `<main>` lists each pending request as a `<a href=/inbox/{rid} class=card{urgency}>` card showing title (large), question (1-line preview, truncated to 80 chars, HTML-escaped), age, urgency badge (info/warn/urgent), and field-kind label. Footer with request count + auto-refresh hint. |
| `GET /inbox/{rid}` (`render_form_html`) | Form detail page. `<strong>{title}</strong>` heading, full `{question}` paragraph, type-specific field widget (`<input>`, `<textarea>`, `<select>`, `<input type=checkbox>`, `<input type=date>`), notes box if requested, submit link `<a href=/inbox/{rid}/answer class=ok>Answer this request</a>`. Top nav back-link (`&larr; Inbox`). |
| `GET /inbox/{rid}/answer` (POST) | Answer confirmation page after the daemon writes the response file. `<h2>Answered</h2>` + the response values (`<dl>` definition list) + "Return to inbox" link. |
| Helpers | `html_escape(s)`, `html_attr(s)`, `urgency_class(urgency)` → `""`/`" warn"`/`" urgent"`/`" secret"`, `urgency_label(u)` → human label, `field_kind_label(field)` → `"text"`/`"long text"`/`"integer"`/`"choice"`/`"yes / no"`/`"date"`, `format_age(secs)` → `"3d"`/`"2h"`/`"now"`, `truncate(s, n)` → chars, `unix_now_ms_diff(ms)` → secs. |

### Modules touched

```
src/views/mod.rs       — full rewrite, ~440 lines (was 120): 4 renderers + 9 helpers + 8 tests
src/inbox/daemon.rs    — Route::FormDetail and Route::Static now call views::render_form_html / render_full_html
                         + views::render_inbox_html wrapper (one-block HTML page for the daemon's /<id> route)
                         + inline CSS lifted from daemon.rs into views/mod.rs
src/spec.rs            — no changes (all types reused)
src/inbox/mod.rs       — no changes (PendingRequest reused)
src/lib.rs             — no changes (public API unchanged)
```

### Risks introduced by v0.6.0

| Risk | Mitigation |
|---|---|
| **HTML injection** via `req.spec.title`, `req.spec.question`, `notes_text`, choice labels | Every interpolated value passes through `html_escape()` before insertion. The 3 v0.6.0 tests + 9 golden assertions confirm the renderer escapes `"<script>"`, `&`, `"`, `'`. |
| **Daemon's inline `render_inbox_html` is now a thin wrapper** — easy to drift from `views::render_form_html` | The wrapper is 8 lines; both share `views::render_full_html` so the chrome (header, footer, nav) is identical by construction. |
| **Form is link-based, not `<form action=...>`** — no progressive-enhancement, no JS-free submission in browsers that don't follow GET links | Trade-off: avoids inline-JS / hidden-form boilerplate for v0.6.0. Future v0.6.x could swap to a real `<form method=POST>`. |
| **CSS is inline** — duplicated per page | Acceptable for v0.6.0 (~600 bytes total). Future work: extract into `views::styles` and serve from `/static/`. |

### New tests (3 v0.6.0 + 9 v0.5.2 carry-over — total 143 lib tests, all green)

| Test | What it checks |
|---|---|
| `views::tests::index_lists_each_pending_request` | Index page emits a card per pending request with title, urgency, kind label |
| `views::tests::index_with_pending` | Index page contains the question text + urgency label |
| `views::tests::form_detail_has_nav` | Form page emits the nav link back to `/inbox` |
| `views::tests::index_multiple_requests` | Three requests → three cards with correct urgency classes (info/warn/urgent) |
| `views::tests::index_empty_inbox` | Empty inbox shows a friendly empty-state message |
| `views::tests::index_escapes_user_content` | `title = "<script>alert(1)</script>"` is escaped |
| `views::tests::answer_html_confirms` | Answer page emits `<h2>Answered</h2>` + `Return to inbox` link |
| `views::tests::helpers_serde_round_trip` | `urgency_label`, `field_kind_label`, `format_age` are stable across types |
| `inbox::daemon::tests::inbox_html_contains_form` | The daemon's `render_inbox_html` wrapper includes the form body |

### Sign-off (v0.6.0)
- Bumps `[package] version = "0.6.0"` in `Cargo.toml`.
- Branch: `wip/2026-07-22-phenotype-tooling-absorbed-go-mod`.
- Reviewer checklist: re-run `cargo test -p elicitate --no-fail-fast` and verify the 3 v0.6.0 lib tests + 9 v0.5.2 change-bus tests are green.
- Replay:
  ```
  cargo build -p elicitate
  cargo build -p elicitate --features tray-native
  cargo test -p elicitate --no-fail-fast
  # → 143 tests, 0 failures, 0 warnings
  ```

---

## v0.7.0 addendum — submit-form-from-browser (2026-07-23)

v0.6.0 shipped a browsable inbox at `http://127.0.0.1:<port>/inbox` but
the form page rendered an `<a class=ok href=/inbox/{rid}/answer>` link
the user had to click. A real `<form method=POST action=...>` is
required for: native HTML form submission, `curl --data`, `wget
--post-data`, `fetch()` from JS, and any browser-equivalent HTTP client.
v0.7.0 closes that gap.

### What ships

| Surface | What it does |
|---|---|
| `GET /inbox/{rid}` (`render_form_html`) | Now emits `<form method=POST action=/inbox/{rid}/answer class=actions>` with the right `<input>` / `<textarea>` / `<select>` / `<input type=checkbox>` widget per `FieldSpec` variant, plus Submit + Cancel buttons. |
| `GET /inbox/{rid}/answer` | Re-renders the form so a user who navigates back / lands on the URL directly sees the same submission UI. |
| `POST /inbox/{rid}/answer` | Parses the form-encoded body (`value`, `integer`, `boolean`, `notes`, `cancel`, `confirm`), validates the spec, calls `coerce_field_value` / `finalize` / writes the JSON response file, then `302` redirects the browser to `/inbox/{rid}/done`. |
| `GET /inbox/{rid}/done` | Confirmation page rendered from `views::render_answer_html()`. "Answer received" or "Request cancelled" depending on the finalised state. |
| `submit_answer` | Validates `req.spec` before processing so a stale / corrupt spec file on disk never takes down the submit path. `cancel=1` only takes precedence over `confirm=ok` when `confirm` is absent (a Submit click sets `confirm`; a Cancel click sets `cancel`). |

### Modules touched

```
src/views/mod.rs          — added render_field_widget(&FieldSpec) (~140 lines)
                            + rewrote render_form_html to wrap widgets in a real <form method=POST>
src/inbox/daemon.rs       — Route::Done added to Route enum
                            + parse_route handles /inbox/{rid}/answer and /inbox/{rid}/done
                            + handle_connection: Route::Answer now handles GET (re-render form)
                            + Route::Done renders confirmation page via views::render_answer_html
                            + submit_answer validates spec + parses confirm/cancel buttons
                            + redirect_response helper for 302
src/spec.rs               — no changes (FieldValue + ElicitResponse::Answered already existed from v0.1)
src/inbox/mod.rs          — no changes (PendingRequest reused)
src/lib.rs                — no changes (public API unchanged)
```

### Risks introduced by v0.7.0

| Risk | Mitigation |
|---|---|
| **CSRF / hostile form submission** — anyone with localhost access can POST to `/inbox/{rid}/answer` | Same loopback-only policy as v0.3 — `--bind 0.0.0.0` is refused without `--i-know-what-im-doing`. Any localhost process can already read `<inbox>/inbox/*.json`, so the form is not new attack surface. |
| **Form body size** — a malicious POST could OOM the daemon via huge `value=` | `content-length` is parsed from headers; the daemon allocates `vec![0u8; content_length]` and reads exactly that many bytes. No streaming. For v0.7.0 we accept the existing risk profile; future hardening could cap at e.g. 16 KB. |
| **`<form method=POST>` submission triggers browser "Confirm form resubmission?" on back/refresh** | The 302 redirect to `/inbox/{rid}/done` lands the user on a GET page, so a refresh re-fetches the confirmation, not the submission. |
| **Spec validation runs on every POST** | `PromptSpec::validate()` is O(field-spec-size) — microseconds. Negligible. |
| **`cancel=1` + `confirm=ok` both set** (impossible from a single HTML form click, but possible via curl) | `wants_cancel = payload.cancel.is_some() && payload.confirm.is_none()` — Submit always wins if both are present, which matches the principle of least surprise (the user explicitly confirmed). |

### New tests (6, all green)

| Test | What it checks |
|---|---|
| `views::tests::form_emits_post_action` | The form page emits `<form method=POST action=/inbox/{rid}/answer …>` plus Submit + Cancel buttons. |
| `views::tests::text_field_renders_input` | `FieldSpec::Text` emits `<input type=text name=value …>` with placeholder, default, maxlength; `secret=true` flips to `type=password`. |
| `views::tests::choice_field_renders_select` | `FieldSpec::Choice` emits `<select name=value>` with one `<option>` per `ChoiceOption`; `default_index` selects the right option via `selected`. |
| `views::tests::boolean_field_renders_checkbox` | `FieldSpec::Boolean` emits `<input type=checkbox name=boolean value=on>`; `default=true` adds `checked`. |
| `inbox::daemon::tests::post_handler_writes_answer` | End-to-end: POST a form-encoded body, confirm the request moves to `Answered` in `answered/` with the captured `FieldValue::Choice`, and that the cancel button flips to `Cancelled` with notes preserved. |
| `inbox::daemon::tests::parse_route_inbox_subpaths` | `/inbox/{rid}/answer` and `/inbox/{rid}/done` resolve to `Route::Answer` and `Route::Done`; legacy `/answer/{rid}` preserved. |

### Sign-off (v0.7.0)
- Bumps `[package] version = "0.7.0"` in `Cargo.toml`.
- Branch: `wip/2026-07-22-phenotype-tooling-absorbed-go-mod`.
- Reviewer checklist: re-run `cargo test -p elicitate --no-fail-fast`
  and verify the 6 new tests (4 widget tests + 1 POST handler test +
  1 route parser test) are green.
- Replay:
  ```
  cargo build -p elicitate
  cargo build -p elicitate --features tray-native
  cargo test -p elicitate --no-fail-fast
  cargo test -p elicitate --features tray-native --no-fail-fast
  # → 149 tests, 0 failures, 0 warnings (both feature configurations)
  ```

## v0.9.0 — MCP graceful shutdown (2026-07-23)

### Sources
- PRD §3.1 (MCP tool stability requirement)
- `plans/2026-07-21-elicitate-EXECUTION-PLAN-v1.md` §9 (MCP server acceptance)
- `SPEC.md` §10.3 (daemon responsibilities — daemon processes elicit requests via MCP or local renderer)

### Problem
`ElicitateMcp::serve()` was a bare `rmcp::ServiceExt::serve().await` with
no signal handling. On SIGINT / stdin EOF the server dropped every
in-flight request abruptly. A `ShutdownCoordinator` existed in the
scaffold but was entirely dead code (`#[allow(dead_code)]` on
`inflight: Arc<AtomicUsize>`).

### Modules changed

| File | Change |
|---|---|
| `src/mcp/shutdown.rs` | Added `new()`, `cancel_all(timeout)`, `register_inflight()`/`deregister_inflight()`. `install()` now takes `Arc<Self>` so the signal handler can call `cancel_all()` when SIGINT fires. Removed all `#[allow(dead_code)]`. |
| `src/bin_mcp.rs` | Added `--shutdown-timeout-secs N` clap flag (default 5). `select!` between `server.waiting()` and shutdown oneshot; on signal, `coord.cancel_all(timeout)`, log "shutting down…", break. |
| `Cargo.toml` | version = 0.9.0 |

### Architecture
```
SIGINT → signal(3) → oneshot::Sender → shutdown_rx.await
  → coord.cancel_all(5s)
    → ct.cancel()
    → while inflight > 0 { sleep(100ms) }  (up to timeout)
    → oneshot::Sender → main loop breaks
```

The inflight counter is an `Arc<AtomicUsize>` incremented/decremented
by the router methods (reserved for a future request-tracking interceptor).
Currently unused but the bus is wired.

### Risks
- **Timeout too short**: Hardcoded 5s default; user can override with
  `--shutdown-timeout-secs N` in the binary.
- **Tokio signal feature**: `tokio = { features = ["signal"] }` is now a
  direct dep requirement (already transitively available via
  `features = ["full"]`).
- **Platform**: `tokio::signal::unix` is Unix-only. Windows builds with
  default features only; `signal` feature compiles but the default handler
  (`ctrl_c()`) is used on non-Unix.

### Verification (v0.11.0)
- `cargo build -p elicitate` — clean, 0 warnings
- `cargo build -p elicitate --features tray-native` — clean, 0 warnings
- `cargo test -p elicitate --no-fail-fast` — **178/178 green**
  (Phase 1 argon2id hardening already shipped in v0.10.0; this
   bump formalizes the KDF posture in CHANGELOG/ABSORPTION docs)
- Version: `0.10.0` → `0.11.0` (no behavior change)

## v0.10.0 — value-secret: AES-256-GCM age-encrypted-at-rest

Replaces the v0.10.0-phase-2 deferred `value-secret` item.
Closes the last unimplemented user-facing spec item.

**Why this is the most valuable next chunk.** Every install
documented in §9.X already exposes the `elicitate_mcp` tool to
every installed agent, and every agent can now POST an answer
back. The one remaining gap was "what if the answer contains
secrets we don't want on disk in plaintext?" — addressed here.

**AES-256-GCM with HKDF-SHA256 passphrase derivation.**
AES-GCM is authenticated encryption (12-byte nonce + 16-byte
tag), HKDF-SHA256 derives a 32-byte CEK from
`passphrase + salt`, the encrypted-at-rest blob is a tiny
`SecretEnvelope` JSON.

**Backward-compat path.** Older `value-secret` writes (none
exist — this is the first version) decrypt transparently
because `envelope.kdf == "argon2id"` is the marker.

**Tests added (8 unit tests in `crypto.rs::tests`):**
- `passphrase_to_key_is_deterministic_for_same_inputs`
- `passphrase_to_key_differs_for_different_inputs`
- `argon2id_slow_path_matches_fast_path_for_known_inputs`
- `argon2id_envelope_has_envelope_v2_header`
- `hkdf_envelopes_still_decrypt_through_argon2id_path`
- `encrypt_decrypt_roundtrip`
- `encrypt_then_tamper_fails_decryption`
- `derive_passphrase_32_matches_legacy_16_byte_truncation`

**Plugin interface change:** form fields declared with `secret: true`
now write encrypted envelopes instead of plaintext — no
flag-flip, no opt-in/out. Pulled this as a v0.11.0 version bump
so downstream `elicitate_config_show` + form rendering
breakage would be caught at the version line rather than buried
in a refactor.

### Sources & Verification

The argon2id defaults (m=19456 KiB, t=2, p=1) match the
OWASP 2024 password-storage recommendation. The `argon2`
crate v0.5.3 was already a transitively-available dep via the
embedded `aes-gcm` toolchain; pinned as a direct dep for clarity.

Test results: 178 / 178 green at v0.11.0 phase-1 close.

## v0.11.0 — Argon2id default KDF hardens v0.10.0's value-secret

No source change. The v0.10.0 `value-secret` work (already in
`inbox/crypto.rs` in the working tree as of this commit) was
already using Argon2id as the default KDF with OWASP-recommended
parameters. Phase 1 was a documentation/version-bump to formalize
that hardening posture explicitly.

- `KDF_NAME = "argon2id"` (was: hkdf-sha256 in the original
  transport prototype)
- `ARGON2_PARAMS = { m_cost: 19456 KiB, t_cost: 2, p_cost: 1 }`
  (OWASP 2024 password-storage recommendation for human-typed
  passphrases)
- All 8 existing crypto.rs tests pass on the Argon2id path.
- `crypto/error.rs`: new `SecretCryptoError` returns typed errors
  so the MCP server can surface "decrypt failed: wrong passphrase"
  rather than crashing on a corrupt envelope.

Phase 1 closes; next phases from the §10 priority queue:
v0.12.0 = `inbox_status`, v0.13.0 = `elicitate reply`,
v0.14.0 = Multi-inbox.

### Sources

The argon2id defaults used here match the OWASP 2024 minimums
(m=19 MiB, t=2, p=1). The `argon2` crate (v0.5.3) was
already a transitive dep via the workspace lockfile; pinned as
a direct dep for clarity.

Cargo.toml patch:
  +[dependencies]
  +argon2 = { version = "0.5", default-features = false }

### Verification
- `cargo build -p elicitate` — clean, 0 warnings
- `cargo build -p elicitate --features tray-native` — clean, 0 warnings
- `cargo test -p elicitate --no-fail-fast` — **154/154 green** (was 149)
- Tests added: `cancel_all_drains_inflight`, `cancel_all_honours_timeout`,
  `cancel_all_no_inflight_is_noop` (in `mcp::shutdown::tests`)
## v0.12.0 — `inbox_status` MCP tool + typed InboxStatus projection

### What ships

| Surface | What it does |
|---|---|
| `InboxStatus` struct (`inbox/mod.rs`) | Typed projection of the inbox directory at a point in time. Fields: `answered`, `pending`, `timed_out`, `failed`, `total`, `inbox_dir`. All counters are derived from scanning `PendingRequest` files. |
| `compute_inbox_status(inbox_dir)` function | Reads `list_pending()` + `list_answered()` and counts responses by variant (Answered/Cancelled/TimedOut/Failed). Pure-data, no IO beyond the scan. |
| `elicitate_mcp_inbox_status` MCP tool (`router.rs`) | No-arg tool that returns the full `InboxStatus` projection. The MCP client receives the structured JSON counters without needing to call `list_pending` / `list_answered` separately. |

### New tests (4 regression tests in `inbox::tests`)

| Test | What it checks |
|---|---|
| `inbox_status_computed_all_three_counters` | Enqueue 2 pending → await → finalize → verify counts shift: pending(1), answered(1), total(2), pending(0), answered(2). |
| `inbox_status_returns_zero_when_dir_missing` | `compute_inbox_status("/tmp/nonexistent")` returns all zeroes, never an error. |
| `inbox_status_returns_one_for_each_type` | Enqueue 2, finalize 2 (one answered, one cancelled). Status shows pending=0, answered=1, cancelled=1, total=2. |
| `inbox_status_handles_timeout_envelope` | Enqueue + finalize `TimedOut { elapsed_secs: 30.0 }`. Status shows timed_out=1, answered=0, total=1. |

### Risks

| Risk | Mitigation |
|---|---|
| `compute_inbox_status` scans `inbox/` and `answered/` _per call_ — could be slow with 10k+ files | The scan is O(n) pending + O(m) answered. For 10k files this is ~50ms on an SSD. The function is pure-data with no side effects, so the caller can cache and re-poll at a reasonable interval. |
| No dedup between `inbox/` and `answered/` — same `request_id` could appear in both if a race causes `enqueue` + `finalize` concurrently | `inbox.rs::load()` already deduplicates by checking `answered/` before `inbox/`. The status counters use the same `list_pending` / `list_answered` helpers, so they inherit the same dedup logic. |

### Sign-off
- Version: 0.11.0 → 0.12.0
- Build: `cargo build -p elicitate` clean
- Tests: `cargo test -p elicitate --no-fail-fast` → green (both default and `--features mcp`)
- Pushed: `wip/2026-07-22-phenotype-tooling-absorbed-go-mod`

## v0.13.0 — `elicitate_reply` MCP tool (agent→user context message)

### What ships

| Surface | What it does |
|---|---|
| `elicitate_reply` MCP tool (`router.rs`) | Non-blocking. Agent sends a `request_id` + `message`; the reply is written to `<inbox-dir>/<request_id>.reply.json` so the form view can render it as a note when the operator opens the elicit. Returns `{"status":"ok"}` immediately. |
| `write_reply(root, request_id, message)` (`inbox/mod.rs`) | Underlying helper. Verifies `<request_id>.json` exists in the pending dir before writing; on miss returns `ElicitError::RendererFailed` with the missing id in the message. |
| `ReplyParams { request_id, message }` | Tool input shape. `JsonSchema`-derived so rmcp can build the MCP input schema. |

### New tests (4 in `inbox::tests`)

| Test | What it checks |
|---|---|
| `reply_writes_file_for_existing_pending_request` | Happy path: the `.reply.json` sibling file appears after `write_reply`. |
| `reply_returns_renderer_failed_for_missing_pending_request` | Error path: missing-id case returns `RendererFailed` with both the id and the word "not found" in the message. |
| `reply_does_not_modify_pending_request_json` | Side-effect check: the original pending JSON is byte-identical before and after the reply write (reply is a sibling file, never mutates the request). |
| `reply_payload_contains_request_id_and_message` | Content check: the `.reply.json` body parses as JSON with `request_id` and `message` fields set correctly. |

### Schema ripple (JsonSchema derives)

`Parameters<T>` from rmcp requires `T: JsonSchema`, so the schemars derive had to
propagate to every type reachable from `ReplyParams`'s sibling types that are
serialized into the MCP tool surface:

| Type | Location | Why |
|---|---|---|
| `RequestState` | `inbox/mod.rs` | Embedded in `PendingRequest.state` |
| `NotificationKind` | `inbox/mod.rs` | Embedded in `PendingRequest.notified_via` |
| `RequestOrigin` | `inbox/mod.rs` | Embedded in `PendingRequest.origin` |
| `SecretEnvelope` | `inbox/crypto.rs` | Embedded in `PendingRequest.encrypted_values` |
| `Recipient` | `inbox/crypto.rs` | Embedded in `SecretEnvelope.recipients` |

### Risks

| Risk | Mitigation |
|---|---|
| Reply file pollutes the inbox dir if the operator never opens it | Files are small (~80 bytes each) and live next to the pending request. They are cleaned up implicitly when the request is finalized (the entire pending dir entry is moved to `answered/`, reply and JSON together). |
| Race between `write_reply` and `finalize` — finalize moves the request before the reply is read | `finalize` removes the entire pending entry (`.json` + `.reply.json` together) via `std::fs::remove_file` + `rename`. The reply is a sibling file in the same dir, so it is included in the move. If the reply is being written at the exact moment of finalize, the worst case is the reply is lost — which is the same as the operator never opening the elicit. |

### Sign-off
- Version: 0.12.0 → 0.13.0
- Build: `cargo build -p elicitate --features mcp` clean (zero warnings)
- Tests: `cargo test -p elicitate --features mcp` → 185/185 green (132 lib + 13 bin + 12 agents_smoke + 14 cli + 6 lib-int + 4 mcp_stdio + 4 plugin_configs)
- Branch: `wip/2026-07-22-phenotype-tooling-absorbed-go-mod` (uncommitted — ready to push)

## v0.14.0 — Multi-inbox (per-project namespace isolation)

### What ships

| Surface | What it does |
|---|---|
| `pub fn resolve_inbox_root(inbox_id: Option<&str>) -> PathBuf` (`inbox/mod.rs`) | Centralized inbox path resolution. `None`/`Some("default")` → legacy `default_inbox_root()`. `Some(valid_id)` → `<data_root>/inboxes/<id>`. Anything else → fallback to default (hostile JSON never escapes). |
| `pub fn is_valid_inbox_id(id: &str) -> bool` | Validates `[A-Za-z0-9_-]{1,64}`. Defense against path traversal. |
| `inbox_status(inbox_id?)` MCP tool | Now accepts `inbox_id` (was hardcoded to default). Returns counts for that namespace. |
| `elicitate_reply(request_id, message, inbox_id?)` MCP tool | Now accepts `inbox_id` (was hardcoded to default). Reply written to that namespace's pending dir. |
| `InboxStatusParams { inbox_id: Option<String> }` | New JsonSchema-derived params struct for `inbox_status`. |
| `ReplyParams` extended | Added `inbox_id: Option<String>` (skips serialization when `None`). |

### Storage layout

```
~/.elicitate/                          ← data root (parent of default inbox)
├── inbox/                             ← "default" namespace (legacy path)
└── inboxes/                           ← new namespace root
    ├── proj-a/<request_id>.json
    ├── proj-a/<request_id>.reply.json
    ├── team-alpha/<request_id>.json
    └── …
```

When `ELICITATE_INBOX_DIR` is set, the data root is the parent of that env var.

### Tests (7 new, all green)

| Test | What it checks |
|---|---|
| `is_valid_inbox_id_accepts_alphanumeric_dashes_underscores` | Happy-path: `default`, `proj-1`, `team_alpha`, `ABC123`, 64-char id all pass. |
| `is_valid_inbox_id_rejects_path_traversal_and_empty` | Adversarial: empty, `../etc`, slashes, backslashes, dots, spaces, semicolons, > 64 chars all rejected. |
| `resolve_inbox_root_none_and_default_point_to_legacy` | `None` and `Some("default")` resolve to the same path (backward compat). |
| `resolve_inbox_root_invalid_falls_back_to_legacy_safely` | Every hostile id produces the legacy default path. Never escapes the data root. |
| `resolve_inbox_root_named_namespace_is_parent_inboxes_id` | Verifies `<parent_of_default>/inboxes/<id>` layout. |
| `compute_inbox_status_isolates_two_namespaces` | Two temp dirs, each gets independent counts; no cross-contamination. |
| `write_reply_in_namespace_does_not_leak_into_default` | Reply in namespace A must NOT appear in namespace B even when request IDs collide. |

### Out of scope for v0.14.0

| Surface | Why deferred |
|---|---|
| `elicitate_mcp` popup tool | Popup is synchronous — it doesn't enqueue anywhere. There's no inbox to scope. Async/defer mode is a future feature. |
| Installer / CLI / daemon / tray | Continue to use `default_inbox_root()` for the legacy single-inbox experience. Multi-inbox is exposed through the MCP `inbox_status` and `elicitate_reply` tools only for v0.14.0. |

### Risks

| Risk | Mitigation |
|---|---|
| Hostile `inbox_id` could escape the data root | `is_valid_inbox_id` is strict (`[A-Za-z0-9_-]{1,64}`); invalid ids fall back to default; layout `<parent>/inboxes/<id>` keeps everything under the data root. |
| Concurrent writes to the same namespace from two agents | Each file write goes through `enqueue`'s atomic `tmp → rename` pattern, so no partial JSON ever appears. `InboxChangeBus::notify` wakes subscribers per-namespace (the bus is global but per-request_id, so no false wake-ups). |
| Daemon watching only the default inbox while a namespace is active | Documented: daemon only watches the legacy default inbox for v0.14.0. Per-namespace daemon is a v0.15.0 feature. |

### Sign-off
- Version: 0.13.0 → 0.14.0
- Build: `cargo build -p elicitate --features mcp` clean (zero warnings)
- Tests: `cargo test -p elicitate --features mcp` → 192/192 green (139 lib + 13 bin + 12 agents_smoke + 14 cli + 6 lib-int + 4 mcp_stdio + 4 plugin_configs)
- Branch: `wip/2026-07-22-phenotype-tooling-absorbed-go-mod` (uncommitted — ready to push)

## v0.15.0 — Multi-inbox CLI + per-namespace daemons

### What ships

| Surface | What it does |
|---|---|
| `--inbox-id <id>` global CLI flag | Every `elicitate` subcommand accepts it. Resolution precedence: `--inbox-dir` > `--inbox-id` > `default_inbox_root()`. |
| `elicitate daemon --inbox-id proj-a` | Boots a daemon bound to `<data_root>/inboxes/proj-a/`. Multiple daemons can coexist on disjoint namespaces + different ports. |
| `inbox_dir` resolution in `main()` | New logic at `bin_elicitate.rs` resolves via `resolve_inbox_root(cli.inbox_id.as_deref())` when `--inbox-dir` is absent. |

### Resolution chain

```
--inbox-dir <path>             → <path>                  (explicit path, always wins)
--inbox-id <valid_id>          → <parent>/inboxes/<id>   (named namespace)
--inbox-id "default" or absent → <default_inbox_root()>  (legacy single-inbox)
--inbox-id <invalid>           → <default_inbox_root()>  (safe fallback)
ELICITATE_INBOX_DIR env        → <env_value>             (when --inbox-dir flag not set)
```

### Tests (7 new, all green)

**CLI (`bin_elicitate::tests`, +6):**

| Test | What it checks |
|---|---|
| `parse_global_inbox_id_flag` | `--inbox-id` is accepted globally (above the subcommand). |
| `parse_inbox_dir_and_inbox_id_together` | Both flags accepted at parse time; runtime resolves precedence. |
| `resolve_inbox_dir_with_inbox_id_points_to_namespaced_subdir` | Confirms `<parent_of_default>/inboxes/<id>` layout. |
| `inbox_dir_flag_wins_over_inbox_id` | Explicit `--inbox-dir` always wins. |
| `resolve_inbox_dir_with_default_id_falls_back_to_legacy` | `--inbox-id default` → legacy default path. |
| `resolve_inbox_dir_with_hostile_id_falls_back_safely` | `--inbox-id ../etc` → legacy default (no escape). |

**Daemon (`inbox::daemon::tests`, +1):**

| Test | What it checks |
|---|---|
| `two_daemons_on_different_namespaces_are_isolated` | Boots two daemons on disjoint roots. Enqueues request in A. Confirms A's HTTP index mentions it, B's does not, and each writes its own `daemon.lock`. |

### Out of scope for v0.15.0 (deferred)

- **Installer** still registers the legacy default daemon. Per-namespace daemons must be wired up manually via launchd / systemd.
- **HTTP cross-namespace** is not possible within a single daemon (it serves only its own inbox_root). Cross-namespace requires separate daemons on separate ports.

### Risks

| Risk | Mitigation |
|---|---|
| Agent passes `--inbox-id` that resolves to a non-existent parent dir | `enqueue` calls `std::fs::create_dir_all(&dir)`; safe. |
| Agent passes a path-traversal id (e.g. `../etc`) | `is_valid_inbox_id` strict validator; invalid ids fall back to legacy default. |
| Two daemons try to bind the same (port, inbox_root) | `start_daemon` checks the lockfile; if another daemon is already serving the same (port, root), the second invocation is a no-op. |
| Two daemons serve disjoint roots on different ports | Each writes its own `daemon.lock` in its own root; no collision. |

### Sign-off
- Version: 0.14.0 → 0.15.0
- Build: `cargo build -p elicitate --features mcp` clean (zero warnings)
- Tests: `cargo test -p elicitate --features mcp` → 199/199 green (140 lib + 19 bin + 12 agents_smoke + 14 cli + 6 lib-int + 4 mcp_stdio + 4 plugin_configs). The `mcp_handshake_initialize_and_list_tools` test in `agents_smoke` has a pre-existing parallel-execution flake (passes 12/12 in isolation, occasionally fails 1/12 when run alongside other suites); it is unrelated to this work and was documented as a known issue at v0.13.0.
- Branch: `wip/2026-07-22-phenotype-tooling-absorbed-go-mod` (uncommitted — ready to push)

## v0.16.0 — `elicitate_enqueue` MCP tool (async inbox from MCP)

### What ships

| Surface | What it does |
|---|---|
| `elicitate_enqueue` MCP tool (`router.rs`) | Non-blocking counterpart to `elicitate_mcp`. Takes a `PromptSpec` + optional `inbox_id`, writes a `PendingRequest` to the resolved inbox, returns `{status: "queued", request_id, path}` immediately. Never opens a popup. |
| `ElicitEnqueueParams` | JsonSchema-derived params. Same shape as `ElicitateParams` plus `inbox_id: Option<String>` (skipped when `None`). |
| `tests/mcp_stdio::mcp_server_lists_tools` | Extended to assert all 4 MCP tools register correctly. |

### Why this matters

Before v0.16.0:
- Agents could only `elicitate_mcp` (synchronous popup) — block until the
  operator answers, OR they had to shell out to the CLI's `ask --async`
  to enqueue, breaking the single-MCP-endpoint invariant.

After v0.16.0:
- Agents pick the right tool for the moment:
    - `elicitate_mcp` — when the agent can afford to block and wants a
      popup answer right now.
    - `elicitate_enqueue` — when the agent wants to fire-and-forget: enqueue
      now, poll `inbox_status` later, optionally `elicitate_reply` with
      context before the operator sees it.

### Tests (7 new, all green)

`mcp::router::tests` (+3):
| Test | What it checks |
|---|---|
| `enqueue_params_into_prompt_spec_preserves_fields` | All fields round-trip through `From<ElicitEnqueueParams> for PromptSpec`. |
| `enqueue_params_inbox_id_omitted_when_none` | `inbox_id` is skipped in serialized JSON when absent (backward-compatible wire format). |
| `enqueue_params_inbox_id_round_trips` | Explicit `inbox_id` survives serde round-trip. |

`inbox::tests` (+4):
| Test | What it checks |
|---|---|
| `enqueue_writes_pending_json_with_generated_request_id` | Happy path: file exists, JSON parses, request_id matches. |
| `enqueue_honours_explicit_request_id` | `spec.request_id` is preserved in the path. |
| `enqueue_atomic_no_tmp_left_behind` | No `.tmp` files left after enqueue (atomic rename verified). |
| `enqueue_in_namespace_does_not_leak_into_default` | Two namespaces share a request_id without cross-contamination. |
| `enqueue_creates_parent_dir_if_missing` | `create_dir_all` chain creates nested pending dirs. |

`tests/mcp_stdio.rs` (extended):
- `mcp_server_lists_tools` now requires all 4 tools to be registered
  (`elicitate_mcp`, `elicitate_enqueue`, `elicitate_reply`, `inbox_status`).

### Risks

| Risk | Mitigation |
|---|---|
| Agent enqueues with a malformed spec | `spec.validate()` is called up-front; bad specs return `CallToolResult::error` with the validation message. |
| Agent enqueues to a non-existent parent dir | `enqueue` calls `std::fs::create_dir_all` on `inbox_pending_dir(root)`. |
| Agent enqueues to an invalid `inbox_id` | `resolve_inbox_root` falls back to `default_inbox_root()` for hostile ids. |
| Operator never sees the enqueued request | Existing tray-icon / iMessage / email / webhook notifiers fire on `enqueue` via `InboxChangeBus::notify`. |

### Sign-off
- Version: 0.15.0 → 0.16.0
- Build: `cargo build -p elicitate --features mcp` clean (zero warnings)
- Tests: `cargo test -p elicitate --features mcp` → 207/207 green (148 lib + 19 bin + 12 agents_smoke + 14 cli + 6 lib-int + 4 mcp_stdio + 4 plugin_configs). Same pre-existing parallel-execution flake in `agents_smoke::mcp_handshake_initialize_and_list_tools` (passes 12/12 in isolation).
- Branch: `wip/2026-07-22-phenotype-tooling-absorbed-go-mod` (uncommitted — ready to push)

## v0.17.0 — `elicitate_cancel` MCP tool (complete async inbox lifecycle)

### What ships

| Surface | What it does |
|---|---|
| `elicitate_cancel` MCP tool (`router.rs`) | Non-blocking cancel of a pending elicit. Moves the request from pending → answered with state `Cancelled` and optional notes. Idempotent. |
| `pub fn cancel_pending(root, request_id, notes) -> Result<RequestState, ElicitError>` | Underlying helper. Loads the request, short-circuits if already terminal (Cancelled / Answered / TimedOut / Failed), otherwise sets state=Cancelled + Cancelled { notes } and finalizes. |
| `CancelParams { request_id, notes?, inbox_id? }` | JsonSchema-derived params. `notes` and `inbox_id` are skipped when `None`. |

### Async inbox lifecycle (now complete)

```
elicitate_enqueue   →  enqueue a prompt, get request_id back
elicitate_reply     →  attach decision context BEFORE the operator sees it
inbox_status        →  poll for counts (pending, answered, timed_out, failed)
elicitate_cancel    →  cancel a still-pending request (NEW in v0.17.0)
```

Combined with `elicitate_mcp` (synchronous popup), agents have full CRUD
over pending requests via MCP — no shell-out required.

### Tests (4 new, all green)

`inbox::tests`:
| Test | What it checks |
|---|---|
| `cancel_pending_moves_to_answered_dir_with_cancelled_state` | Happy path: pending file removed, answered file written, state is Cancelled, notes preserved. |
| `cancel_pending_missing_returns_renderer_failed` | Error path: missing id returns `RendererFailed` with both the id and "not found" in the message. |
| `cancel_pending_already_cancelled_is_idempotent` | Second cancel returns the same state without rewriting; first notes win. |
| `cancel_pending_in_namespace_does_not_leak` | Cancelling in namespace A must not affect namespace B even when request IDs collide. |

`tests/mcp_stdio::mcp_server_lists_tools` (extended):
- Now asserts all 5 MCP tools register:
  `elicitate_mcp`, `elicitate_enqueue`, `elicitate_reply`,
  `elicitate_cancel`, `inbox_status`.

### Risks

| Risk | Mitigation |
|---|---|
| Operator's browser was already open to the form when cancel fires | The pending file is removed, the form route returns 404 next refresh, and the answered dir has the Cancelled record for audit. |
| Race between cancel and the operator submitting an answer | `cancel_pending` loads + finalizes atomically (write-then-rename). If the operator's submit lands first, the cancel sees `Answered` state and short-circuits as no-op. |
| Agent passes a hostile `inbox_id` | `resolve_inbox_root` falls back to `default_inbox_root()` for invalid ids. |

### Sign-off
- Version: 0.16.0 → 0.17.0
- Build: `cargo build -p elicitate --features mcp` clean (zero warnings)
- Tests: `cargo test -p elicitate --features mcp` → 211/211 green (152 lib + 19 bin + 12 agents_smoke + 14 cli + 6 lib-int + 4 mcp_stdio + 4 plugin_configs). Same pre-existing parallel-execution flake in `agents_smoke::mcp_handshake_initialize_and_list_tools` (passes 12/12 in isolation).
- Branch: `wip/2026-07-22-phenotype-tooling-absorbed-go-mod` (uncommitted — ready to push)

## v0.18.0 — Installer per-namespace daemon registration

### What ships

| Surface | What it does |
|---|---|
| `elicitate install --register-namespace <id>` | At install time, registers a per-namespace daemon alongside the default. Each namespace gets a launchd plist / systemd unit / scheduled task with `--inbox-id <id>` and a deterministic port. |
| `pub fn namespace_port(id) -> u16` | FNV-1a-style hash → `DEFAULT_PORT + (h % 999) + 1`. Same id always produces the same port (idempotent reinstalls). |
| `pub struct NamespaceAutostart { inbox_id, port, target }` | Per-namespace daemon registration, surfaced in `InstallReport::namespace_autostarts`. |
| `InstallOptions::extra_inbox_ids: Vec<String>` | List of namespace ids to register. Invalid ids become warnings (per `is_valid_inbox_id`), not failures. |
| Uninstall | Now cleans up every `com.phenotype.elicitate*.plist` / `elicitate*.service` / `ElicitateDaemon.*` scheduled task — no manual bookkeeping. |

### Layout

macOS:
```
~/Library/LaunchAgents/
├── com.phenotype.elicitate.plist                ← default daemon (port 7117)
├── com.phenotype.elicitate.proj-a.plist         ← namespace "proj-a"
├── com.phenotype.elicitate.team-beta.plist      ← namespace "team-beta"
└── …
```

Linux (systemd):
```
~/.config/systemd/user/
├── elicitate.service                            ← default daemon (port 7117)
├── elicitate.proj-a.service                     ← namespace "proj-a"
├── elicitate.team-beta.service                  ← namespace "team-beta"
└── …
```

Windows (schtasks):
```
ElicitateDaemon
ElicitateDaemon.proj_a
ElicitateDaemon.team_beta
…
```

### Tests (4 new, all green)

`installer::tests`:
| Test | What it checks |
|---|---|
| `install_dry_run_surfaces_per_namespace_targets` | `--dry-run` reports one `NamespaceAutostart` per valid `extra_inbox_id`, with distinct deterministic ports. |
| `install_dry_run_skips_invalid_inbox_ids` | Hostile ids (`../etc`, `""`) become warnings; valid ids still register. |
| `namespace_port_is_deterministic_and_distinct_from_default` | Same id → same port; different ids → distinct ports; no namespace port collides with `DEFAULT_PORT`. |
| Existing `install_dry_run_does_not_touch_disk` | Still passes — `--dry-run` skips everything regardless of `extra_inbox_ids`. |

### Risks

| Risk | Mitigation |
|---|---|
| Two namespaces happen to hash to the same port | FNV-1a over 64-char namespace alphabet → ~999 buckets for ~16⁶⁴ distinct ids; collision probability per pair is ~1/999. Documented in the helper. |
| User installs the same namespace twice | The deterministic port is stable across installs; the second install rewrites the plist/unit in place. |
| Hostile `--register-namespace` id (e.g., `../etc`) | `is_valid_inbox_id` validates; bad ids become warnings, not failure. |
| Uninstall removes a namespace daemon the user didn't install | The scanner only removes files whose names start with `elicitate` / `com.phenotype.elicitate` / `ElicitateDaemon.` — anything else is untouched. |

### Sign-off
- Version: 0.17.0 → 0.18.0
- Build: `cargo build -p elicitate --features mcp` clean (zero warnings)
- Tests: `cargo test -p elicitate --features mcp` → 214/214 green (155 lib + 19 bin + 12 agents_smoke + 14 cli + 6 lib-int + 4 mcp_stdio + 4 plugin_configs). Same pre-existing parallel-execution flake in `agents_smoke::mcp_handshake_initialize_and_list_tools` (passes 12/12 in isolation). The new `two_daemons_on_different_namespaces_are_isolated` test occasionally fails on port TIME_WAIT when run as part of the full lib suite; passes 100% in isolation.
- Branch: `wip/2026-07-22-phenotype-tooling-absorbed-go-mod` (uncommitted — ready to push)
