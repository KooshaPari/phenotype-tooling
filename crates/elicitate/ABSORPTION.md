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
