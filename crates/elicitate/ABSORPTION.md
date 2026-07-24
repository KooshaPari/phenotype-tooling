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

## v0.4.0 addendum — tray icon (tray-native feature)

### New modules
| Module           | Purpose                                                                    |
| ---------------- | -------------------------------------------------------------------------- |
| `tray`           | `Tray` trait, `MenuAction`, `build_tray(cfg)` dispatcher                   |
| `tray::native`   | macOS `NSStatusItem` + Windows `Shell_NotifyIcon` via `tray-icon` 0.24     |

### Feature flags
- `--features tray-native` — enables real native tray icon (macOS `NSStatusItem`,
  Windows `Shell_NotifyIcon`). Without the feature, `NoopTray` is used.
- `elicitate daemon --no-tray` — disable even if compiled with the feature.

### Sources considered
| Source              | Decision | Reason                                                |
| ------------------- | -------- | ----------------------------------------------------- |
| `tray-icon` 0.24.1  | Adopt    | Powers tauri/wry; cross-platform; well-maintained.    |
| `objc2-app-kit` 0.3 | Adopt    | Required by tray-icon on macOS.                       |
| `windows-sys` 0.61  | Adopt    | Required by tray-icon on Windows.                     |

### Risks
- `TrayIcon` is `!Send` on macOS (holds Objective-C refs). Mitigated by channel-based
  architecture: the `TrayIcon` lives on a dedicated owner thread, commands go via
  `mpsc::Sender`, events come back via `mpsc::Receiver`.

### Verification
- `cargo build -p elicitate --features tray-native` — clean.
- `cargo test -p elicitate` — still 108+ tests green.

---

## v0.5.0 addendum — TUI inbox viewer

### New modules
| Module | Purpose |
| ------ | ------- |
| `tui`  | `ViewerConfig`, `InboxEntry`, `Keymap`, `snapshot_inbox()`, `run_tui()` |

### Dependencies added
- `ratatui 0.30` + `crossterm 0.29` as direct deps (always compiled — TUI is the canonical local UX).

### CLI changes
- `elicitate inbox --tui` — launches the split-pane terminal viewer.
- `elicitate tui` — shorthand alias.
- `--poll-ms` configurable (default 1000).

### Risks
- ratatui requires a terminal; falls back gracefully when `TERM=dumb` or stdin is not a TTY.
- Keybindings rebindable via `ELICITATE_TUI_KEYMAP_<KEY>=<action>` env vars.

### Verification
- `cargo test -p elicitate` → 129/129 green (14 new TUI tests).

---

## v0.5.1 addendum — open-inbox UX + tray plumbing fixes

### Fixes
1. **Tray badge/tooltip never updated** — owner thread was dropping `SetBadge`/`SetTooltip`.
2. **`tray_click_url()` hardcoded `127.0.0.1:7117`** — daemon now threads its actual port.
3. **`inbox --open` hardcoded port** — new `inbox_live_url(root)` reads lockfile + TCP probe.

### New CLI
- `elicitate open [--latest] [--spawn-if-missing] [--print-only]`.
- `elicitate daemon --auto-open-browser`.
- Public API: `inbox_live_url`, `inbox_read_lockfile`, `open_in_default_browser`.

### Verification
- `cargo test -p elicitate` → 133/133 green.

---

## v0.5.2 addendum — InboxChangeBus + TUI --follow

### New modules
| Module               | Purpose                                                    |
| -------------------- | ---------------------------------------------------------- |
| `inbox::change`      | `InboxChangeBus`, `InboxWatcher` (crossbeam-channel-based) |

### Changes
- `enqueue()` / `finalize()` call `bus::notify()` after atomic rename.
- `tui::run()` accepts `follow: bool` — subscribes watcher when true.
- `inbox --tui --follow / --no-follow` flag (default: `--follow`).
- `crossbeam-channel 0.5.16` as direct dep.

### Verification
- `cargo test -p elicitate` → 140/140 green (7 new change-bus tests).

---

## v0.6.0 addendum — web frontend (index + form detail + answer)

### Changes
- `views::render_inbox_index_html` — browsable pending-requests index page with cards,
  urgency badges, time-since-queued.
- `views::render_form_html` — wraps navbar linking to `/inbox`, full title + question.
- `views::render_answer_html` — confirmation page with "Return to inbox".
- New helpers: `html_escape`, `html_attr`, `format_age`, `truncate`, `urgency_class`,
  `urgency_label`, `field_kind_label`.

### Verification
- `cargo test -p elicitate` → 143/143 green (+3 new view tests).

---

## v0.7.0 addendum — submit form from browser

### Changes
- `render_form_html` now emits `<form method=POST action=/inbox/{rid}/answer>` with
  `<input>`, `<textarea>`, `<select>` per `FieldSpec` variant.
- `Route::Answer(rid)` handles both GET (show form) and POST (parse form-urlencoded,
  validate, write answer JSON, redirect to `/inbox/{rid}/done`).
- `Route::Done(rid)` — post-submit confirmation page.
- New types: `FieldValue`, `ElicitResponse::Answered`.

### Verification
- `cargo test -p elicitate` → 149/149 green (+6 new tests).

---

## v0.8.0 addendum — wire /inbox to web frontend

### Changes
- `Route::Index` now calls `render_inbox_index_html(&requests)` instead of `simple_text`.
- `Route::Static` serves CSS with `text/css; charset=utf-8`, retires `index.html` alias,
  returns real 404 for unknown paths.
- `write_response` accepts `content_type` parameter.

### Verification
- `cargo test -p elicitate` → 149/149 green.

---

## v0.9.0 addendum — MCP graceful shutdown

### Changes
- `ShutdownCoordinator::new(timeout)` + `install()` spawns SIGINT handler that calls
  `cancel_all()` to drain inflight requests.
- `bin_mcp.rs`: `select!` between `server.waiting()` and shutdown signal.
- `elicitate-mcp --shutdown-timeout-secs` flag (default 5).

### Verification
- `cargo test -p elicitate` → 149/149 green.
