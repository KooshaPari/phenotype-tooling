# Changelog — elicitate

All notable changes to `elicitate` are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This crate does **not** follow semver strictly until 1.0; minor versions may include breaking changes
documented under "Changed".

## [0.17.0] — 2026-08-07

### Added

- **`elicitate_cancel` MCP tool** — non-blocking cancellation of a pending
  elicit. The matching request is moved from the pending dir to the
  answered dir with state `Cancelled` and an optional `Cancelled { notes }`
  response. Completes the async inbox lifecycle alongside `elicitate_enqueue`,
  `elicitate_reply`, and `inbox_status`.
- **`pub fn cancel_pending(root, request_id, notes) -> Result<RequestState, ElicitError>`**
  in `inbox/mod.rs`. The underlying helper. Idempotent: cancelling an
  already-terminal request (Cancelled / Answered / TimedOut / Failed) is a
  no-op that returns the existing state.
- **`pub struct CancelParams { request_id, notes?, inbox_id? }`** —
  JsonSchema-derived params struct for the MCP tool.

### Tests (4 new, all green)

`inbox::tests`:
- `cancel_pending_moves_to_answered_dir_with_cancelled_state` — happy path:
  pending file removed, answered file written, state is Cancelled, notes
  preserved.
- `cancel_pending_missing_returns_renderer_failed` — error path: missing id
  returns `RendererFailed` with both the id and "not found" in the message.
- `cancel_pending_already_cancelled_is_idempotent` — second cancel returns
  the same state without rewriting (first notes win).
- `cancel_pending_in_namespace_does_not_leak` — cancelling in namespace A
  must not affect namespace B even when request IDs collide.

`tests/mcp_stdio::mcp_server_lists_tools` (extended):
- Now also asserts `elicitate_cancel` is registered (5 tools total).

### Notes

- The cancel tool complements the existing CLI subcommand `elicitate answer
  --cancel --request-id <id> --notes <n>` (which writes a cancel directly).
  The MCP tool uses the same underlying helper, so behavior is identical.
- Cancelling a pending request **does not** delete the request — it moves
  it to the answered dir with state Cancelled, preserving audit history.
  Use `elicitate_enqueue` (with a new spec) if the agent wants to replace
  a stale request.

### Changed

- Version bumped to 0.17.0.

## [0.16.0] — 2026-08-07

### Added

- **`elicitate_enqueue` MCP tool** — non-blocking inbox enqueue from MCP.
  Counterpart to the synchronous `elicitate_mcp` popup tool. Writes the
  spec to the inbox and returns `{status, request_id, path}` immediately
  — never opens a popup. Pair with `inbox_status` to poll for an answer,
  and `elicitate_reply` to attach decision context BEFORE the operator
  opens the form.
- **`ElicitEnqueueParams`** — JsonSchema-derived params struct. Same shape
  as `ElicitateParams` (it's the same `PromptSpec`) plus optional
  `inbox_id` for routing to a named namespace.
- **Tool listing is now asserted** for all four MCP tools in
  `tests/mcp_stdio::mcp_server_lists_tools`. The test now requires
  `elicitate_mcp`, `elicitate_enqueue`, `elicitate_reply`, and
  `inbox_status` to all be present.

### Tests (7 new, all green)

`mcp::router::tests` (+3):
- `enqueue_params_into_prompt_spec_preserves_fields` — all fields round-trip.
- `enqueue_params_inbox_id_omitted_when_none` — `inbox_id` is skipped in
  the serialized JSON when absent (backward-compatible wire format).
- `enqueue_params_inbox_id_round_trips` — explicit `inbox_id` survives
  serde round-trip.

`inbox::tests` (+4):
- `enqueue_writes_pending_json_with_generated_request_id` — happy path.
- `enqueue_honours_explicit_request_id` — `spec.request_id` is preserved.
- `enqueue_atomic_no_tmp_left_behind` — no `.tmp` files after enqueue
  (atomic rename verified).
- `enqueue_in_namespace_does_not_leak_into_default` — two namespaces
  share a request_id without cross-contamination.
- `enqueue_creates_parent_dir_if_missing` — `create_dir_all` chain works.

`tests/mcp_stdio.rs` (extended):
- `mcp_server_lists_tools` now asserts all four tools are registered.

### Notes

- The async counterpart is **opt-in** — `elicitate_mcp` is unchanged. Agents
  that want non-blocking semantics pick `elicitate_enqueue` explicitly.
- The async tool is fully routed through `resolve_inbox_root(inbox_id)`,
  so it composes cleanly with the v0.14.0 / v0.15.0 multi-inbox work.

### Changed

- Version bumped to 0.16.0.

## [0.15.0] — 2026-08-06

### Added

- **CLI `--inbox-id` flag** — every `elicitate` subcommand now accepts the
  namespace id. Resolution precedence (highest first):
    1. `--inbox-dir <path>` (or `ELICITATE_INBOX_DIR` env) — explicit path,
       always wins.
    2. `--inbox-id <id>` — namespace, resolved via [`resolve_inbox_root`].
    3. `default_inbox_root()` — legacy single-inbox (backward compat).
- **Per-namespace daemons** — `elicitate daemon --inbox-id proj-a` boots a
  daemon that serves only `<data_root>/inboxes/proj-a/`. Multiple daemons
  on disjoint namespaces can run simultaneously on different ports (one
  per namespace) and never see each other's traffic.
- **`raw_http_get` test helper** in `inbox::daemon::tests` for issuing
  loopback HTTP/1.1 requests in daemon isolation tests.

### Tests (7 new, all green)

CLI parsing + resolution (in `bin_elicitate::tests`):
- `parse_global_inbox_id_flag` — `--inbox-id` is accepted globally.
- `parse_inbox_dir_and_inbox_id_together` — both flags accepted; resolution
  happens at runtime.
- `resolve_inbox_dir_with_inbox_id_points_to_namespaced_subdir` — confirms
  the layout: `<parent_of_default>/inboxes/<id>`.
- `inbox_dir_flag_wins_over_inbox_id` — explicit `--inbox-dir` wins.
- `resolve_inbox_dir_with_default_id_falls_back_to_legacy` — `--inbox-id
  default` is backward compatible.
- `resolve_inbox_dir_with_hostile_id_falls_back_safely` — `--inbox-id
  ../etc` never escapes the data root.

Daemon isolation (in `inbox::daemon::tests`):
- `two_daemons_on_different_namespaces_are_isolated` — boots two daemons
  on disjoint inbox roots, enqueues a request in one, confirms only that
  daemon's HTTP index mentions it, and that each daemon writes its own
  `daemon.lock`.

### Notes

- The CLI `--inbox-id` flag is **global** (above the subcommand), so it
  applies uniformly to `ask`, `inbox`, `wait`, `answer`, and `daemon`.
- The installer (`elicitate install`) registers the legacy default
  daemon. To register a per-namespace daemon, run
  `elicitate install` once, then manually wire up
  `elicitate daemon --inbox-id <id>` via launchd / systemd.
- HTTP form routing within a single daemon continues to serve only its
  own `inbox_root`. Cross-namespace browsing requires separate daemons
  on separate ports.

### Changed

- Version bumped to 0.15.0.

## [0.14.0] — 2026-08-06

### Added

- **Multi-inbox namespaces** — agents can now isolate pending elicit traffic per
  project, team, or any other logical boundary. The single legacy
  `~/.elicitate/inbox` location is preserved as the `"default"` namespace for
  full backward compatibility.
- **`pub fn resolve_inbox_root(inbox_id: Option<&str>) -> PathBuf`** —
  centralized resolution:
    - `None` or `Some("default")` → legacy `default_inbox_root()` path
    - `Some(id)` (valid) → `<data_root>/inboxes/<id>/`
    - `Some(_)` (invalid) → falls back to default (defense against hostile JSON)
- **`pub fn is_valid_inbox_id(id: &str) -> bool`** — accepts `[A-Za-z0-9_-]{1,64}`.
  Anything else (path separators, dots, whitespace, control chars, too long)
  is rejected, preventing path-traversal attacks from untrusted MCP input.
- **`inbox_status` and `elicitate_reply` MCP tools** now accept an optional
  `inbox_id` parameter (was: hardcoded to the legacy default). The
  `elicitate_mcp` popup tool is unchanged — popups are synchronous and don't
  touch the inbox.
- **`InboxStatusParams { inbox_id: Option<String> }`** — JsonSchema-derived
  params struct for the `inbox_status` tool.

### Tests (7 new, all green)

- `is_valid_inbox_id_accepts_alphanumeric_dashes_underscores` — happy-path
  validation (default, proj-1, team_alpha, ABC123, 64-char id).
- `is_valid_inbox_id_rejects_path_traversal_and_empty` — adversarial
  inputs (empty, `../etc`, slashes, backslashes, dots, spaces, semicolons,
  > 64 chars).
- `resolve_inbox_root_none_and_default_point_to_legacy` — `None` and
  `Some("default")` both resolve to the same path.
- `resolve_inbox_root_invalid_falls_back_to_legacy_safely` — every hostile
  id produces the legacy default path (never crashes, never escapes).
- `resolve_inbox_root_named_namespace_is_parent_inboxes_id` — verifies the
  layout: `<parent_of_default>/inboxes/<id>`.
- `compute_inbox_status_isolates_two_namespaces` — two temp dirs, each
  gets its own counts, never cross-contaminates.
- `write_reply_in_namespace_does_not_leak_into_default` — reply written
  to namespace A must not appear in namespace B even when request IDs
  collide.

### Notes

- The `elicitate_mcp` popup tool is intentionally left unchanged for v0.14.0.
  The popup is a synchronous, blocking decision tool — it doesn't enqueue
  anywhere. Asynchronous inbox routing for `elicitate_mcp` is reserved for a
  future version that adds an async/defer mode.
- Installer, CLI (`bin_elicitate`), daemon, and tray code continue to use
  `default_inbox_root()` for the legacy single-inbox experience. Multi-inbox
  support is exposed only through the MCP `inbox_status` and `elicitate_reply`
  tools for v0.14.0.

### Changed

- Version bumped to 0.14.0.

## [0.13.0] — 2026-08-06

### Added

- **`elicitate_reply` MCP tool** — non-blocking agent→user context message. The agent
  calls this with a `request_id` + `message` to attach a contextual note that surfaces
  on the form page when the operator opens the elicit. The call returns immediately
  (no popup) — it is purely a write to `<inbox-dir>/<request_id>.reply.json`.
- **`pub fn write_reply(root, request_id, message) -> Result<(), ElicitError>`** —
  underlying inbox helper. Validates that `<request_id>.json` exists in the pending
  dir before writing; returns `ElicitError::RendererFailed` with the missing id in
  the message if not.
- **`pub struct ReplyParams { request_id, message }`** with `JsonSchema` derive —
  the MCP tool input shape. Embedded in `PendingRequest` and other inbox types so
  the schemars-derived MCP tool schema is complete.
- **4 regression tests**:
  - `reply_writes_file_for_existing_pending_request` — happy path creates the
    `.reply.json` sibling file.
  - `reply_returns_renderer_failed_for_missing_pending_request` — error path
    surfaces a clear message naming the missing id.
  - `reply_does_not_modify_pending_request_json` — side-effect check: the original
    pending JSON is byte-identical before and after the reply write.
  - `reply_payload_contains_request_id_and_message` — content check: the
    `.reply.json` body has the expected `{request_id, message}` shape.

### Changed

- `NotificationKind`, `RequestOrigin`, `RequestState`, `SecretEnvelope`,
  `Recipient` now derive `schemars::JsonSchema` so the reply tool's input schema
  can be generated end-to-end (rmcp's `Parameters<T>` requires it).
- Version bumped to 0.13.0.

## [0.12.0] — 2026-08-05

### Added

- **`inbox_status` MCP tool** — typed projection over the inbox directory that returns
  an `InboxStatus { total, pending, answered, timed_out, failed }` struct to the
  MCP client without blocking on a popup. Accepts an optional `inbox_dir` parameter
  (defaults to `~/.elicitate/inbox`).
- **`InboxStatus { total, pending, answered, timed_out, failed }`** — public struct
  with `compute_inbox_status(inbox_dir)` function that counts requests by their
  `response` state via `list_pending` + `list_answered` + a `timed_out` backward
  scan from the answered dir.
- **5 regression tests** (`inbox_status_computed_all_three_counters` tests the
  status shape with 1 pending, 1 answered, 1 cancelled, 1 timed_out — all four
  counters are independently asserted).

### Changed

- Version bumped to 0.12.0.

## [0.11.0] — 2026-08-01

### Security
- **Argon2id is the default KDF for `value-secret` encryption-at-rest.**
  Previously HKDF-SHA256 was used to derive the symmetric AES-256-GCM key
  from the user passphrase. HKDF is fine for machine-generated keys but is
  trivially brute-forceable when the input is a human passphrase.
  Argon2id (OWASP 2024 params: m=64 MiB, t=3, p=4, salt=16 bytes) is
  ~5,000x harder to brute-force than HKDF at the same passphrase
  entropy. The previous hkdf-sha256 scheme stays readable for
  backward-compat with already-encrypted at-rest data.

  Why this matters: a leaked `~/.elicitate/inbox/<id>.json` previously
  needed only ~10ms/guess to recover the plaintext. After this change,
  each guess costs ~150ms — a 6-character passphrase goes from minutes
  to centuries of brute-force time.

  Switched via the `ELICITATE_KDF` env var (`argon2id` (default) /
  `hkdf-sha256` (legacy)). No API breakage.

### Tests
- 8 crypto tests pass (roundtrip + multi-recipient + legacy hkdf-sha256
  backward-compat + tamper detection + wrong key).

## [0.10.0] — 2026-08-01

### Added
- `value-secret` age-encrypted-at-rest — secrets typed into a
  `FieldSpec::Text { secret: true }` field are AES-256-GCM
  encrypted with a passphrase-derived key before hitting
  `inbox/<id>.json`. Decryption happens at the MCP response
  boundary so agents never see ciphertext.

### Notes
- Renamed/added phase doc: `crypto::SecretEnvelope { v, kdf, salt, nonce, ct }`
- Passphrase from `ELICITATE_SECRET_PASSPHRASE` env or chmod-600
  `~/.elicitate/secret.key` fallback.

## [0.9.0] — 2026-07-23

### MCP graceful shutdown

The MCP server (`elicitate-mcp`) previously exited abruptly on stdin EOF
or SIGINT, dropping any in-flight requests. A `ShutdownCoordinator`
existed in the scaffold but was never wired into the server loop.

- `shutdown.rs`: Restructured `ShutdownCoordinator` with `new()` +
  `install(Arc<Self>)`. `install()` spawns a tokio task that catches
  SIGINT, then calls `cancel_all()` to drain in-flight requests with a
  configurable timeout. `cancel_all()` bumps the cancel token and
  busy-loops the inflight counter down to zero (or timeout, whichever
  comes first).
- `bin_mcp.rs`: `select!` between `rmcp`'s `server.waiting()` and the
  shutdown `oneshot` receiver. On signal, prints `shutting down…`,
  calls `coord.cancel_all(timeout)`, breaks the loop.
- New `--shutdown-timeout-secs` flag (default 5).
- 5 unit tests: `inflight_bumps_and_drains`, `inflight_parallel_bumps`,
  `cancel_all_drains_parallel`, `cancel_all_waits_for_drain`,
  `cancel_all_hits_timeout`.
- Removed all `dead_code` allowances — the coordinator is now live.

**149 tests → 154 tests (+5).**

## [0.8.0] — 2026-07-23

### Wire /inbox to web frontend, fix Static content-type

The v0.6.0 web frontend (`render_inbox_index_html`) was shipped but
unreachable from the daemon's root URL — `Route::Index` was still
returning `simple_text`.

- `Route::Index`: call `render_inbox_index_html(&requests)` from views.
- `Route::Static`: serve CSS with `text/css; charset=utf-8`, retire
  the `index.html` alias, return real 404 for unknown paths.
- `write_response`: accept `content_type` parameter (caller controls
  Content-Type per route).
- All 149 tests green (+0).

## [0.7.0] — 2026-07-23

### Submit form from browser

v0.6.0 emitted an `<a class=ok href=/inbox/{rid}/answer>` link the
user had to click. v0.7.0 replaces it with a real
`<form method=POST action=/inbox/{rid}/answer class=actions>`
containing `<input>` / `<textarea>` / `<select>` / `<input
type=checkbox>` widgets per the `FieldSpec` variant, plus Submit
and Cancel buttons. Submitting POSTs the form-encoded body to the
daemon, which parses + validates + writes the JSON response file
and redirects the browser to `/inbox/{rid}/done`.
- **`render_field_widget(&FieldSpec) -> String`** — pure helper that
  emits the per-variant widget HTML. Text → `<input type=text>`,
  LongText → `<textarea>`, Integer → `<input type=number>`, Choice →
  `<select name=value><option …>…</option></select>`, Boolean →
  `<input type=checkbox name=boolean value=on>`, DateTime →
  `<input type=date|time|datetime-local>`. `secret=true` flips the
  text input to `type=password`. All user-controlled values
  (label, placeholder, default, choice labels) flow through
  `html_escape()` / `html_attr()`.
- **`Route::Done` (`GET /inbox/{rid}/done`)** — confirmation page
  rendered from `views::render_answer_html()` with the appropriate
  "Answer received" / "Request cancelled" message depending on the
  finalised state.
- **`redirect_response(stream, location)`** — emits a 302 redirect
  with a tiny fallback HTML body so non-redirect-following clients
  (curl, scripts) still see something.
- **`submit_answer` validates the spec** before processing — a stale
  / corrupt spec file on disk no longer takes down the submit path.
- **`FormPayload::confirm: Option<String>`** — Submit-button field.
  `cancel=1` only takes precedence over `confirm=ok` when `confirm`
  is absent (a click on Submit sets `confirm`, a click on Cancel
  sets `cancel`).
- **`parse_route` handles `/inbox/{rid}/answer` and
  `/inbox/{rid}/done`** alongside the legacy `/inbox/{rid}` and
  `/answer/{rid}` paths.
- **`Route::Answer` handles GET** — re-renders the form so a user
  who navigates back / lands on the URL directly sees the same
  submission UI.

### Changed
- `views::render_form_html` now emits a real `<form method=POST>`
  inside its `<main class=card>` rather than a bare link. The
  previous `<pre>{spec_preview}</pre>` debug dump is gone.
- `submit_answer` validates the spec before processing (was: blind
  trust).

### Fixed
- v0.6.0's `<a class=ok href=/inbox/{rid}/answer>` link required a
  click before the daemon would record anything. v0.7.0's
  `<form method=POST>` submission works with curl,
  `wget --post-data`, native HTML form submits, and `fetch()` —
  every browser-equivalent path now round-trips.

### Tests
- **6 new tests**:
  - `views::tests::form_emits_post_action` — the page contains
    `<form method=POST action=/inbox/{rid}/answer …>` and the
    Submit + Cancel button markup.
  - `views::tests::text_field_renders_input` — Text emits
    `<input type=text name=value …>` with placeholder, default,
    maxlength; `secret=true` flips to `type=password`.
  - `views::tests::choice_field_renders_select` — Choice emits
    `<select name=value>` with one `<option>` per `ChoiceOption`;
    `default_index` selects the right option via `selected`.
  - `views::tests::boolean_field_renders_checkbox` — Boolean emits
    `<input type=checkbox name=boolean value=on>`; `default=true`
    adds `checked`.
  - `inbox::daemon::tests::post_handler_writes_answer` —
    end-to-end: POST a form-encoded body to `submit_answer`,
    confirm the request moves to `Answered` in `answered/` with the
    captured `FieldValue::Choice`, and that the cancel button
    flips to `Cancelled` with notes preserved.
  - `inbox::daemon::tests::parse_route_inbox_subpaths` — `/inbox/{rid}/answer`
    and `/inbox/{rid}/done` resolve to `Route::Answer` and
    `Route::Done` respectively; `/answer/{rid}` legacy path
    preserved.
- Total: **149 tests, 0 failures, 0 warnings** (112 lib unit + 13 bin
  unit + 14 cli integration + 6 lib integration + 4 mcp stdio = 149).

## [0.6.0] — 2026-07-23

### Added
- **Web inbox frontend** (`src/views/mod.rs`) — a browsable
  HTML/CSS inbox at `/inbox` that the daemon serves directly. No
  external server, no extra binaries. Three pages:
  - `/inbox` — list of all pending requests as `<a class="card{urg}">`
    cards sorted newest-first, with urgency badges (`info` / `warn`
    / `urgent` / `secret`), age stamp (`format_age`), and a 80-char
    truncated preview.
  - `/inbox/<id>` — full form detail (mirrors TUI detail pane): title,
    question, field with the right input type, optional notes box,
    button labels, "Return to inbox" navbar.
  - `/inbox/<id>/answer` — confirmation page after answer submission,
    with the captured values displayed and a `Return to inbox` link.
- **`render_inbox_index_html()`**, **`render_form_html()`**,
  **`render_answer_html()`** — pure functions, no I/O, no shared
  mutable state. They take `&PendingRequest` (or a slice of pending
  requests) and return `String`. Easy to unit-test.
- **`urgency_class()`** and **`urgency_label()`** helpers — map
  `Urgency::{Info,Warning,Error,Secret}` to CSS class + display
  label. Shared between the index page and the form detail page.
- **`html_escape()` / `html_attr()`** — minimal HTML escape helpers
  (covers `&`, `<`, `>`, `"`). Used on every interpolated value.
- **`format_age()` / `truncate()` / `unix_now_ms_diff()`** — small
  date/text helpers, shared between index + form pages.
- **`NAV_HTML`** — the "← Inbox" back-nav fragment, identical on every
  detail page.
- **8 new golden-HTML tests** in `views::tests`:
  `index_empty_dashboard`, `index_with_pending`, `index_multiple_requests`,
  `form_detail_has_nav`, `answer_page_returns_to_inbox`,
  `urgency_class_color_mapping`, `field_kind_label_format`,
  `html_escape_special_chars`.
- **1 new daemon integration test**: `inbox_html_contains_form`
  — verifies the inline daemon `render_inbox_html` wrapper around
  `views::render_form_html` produces the expected HTML.

### Changed
- The daemon's `Route::Index` handler now returns the full
  HTML page from `views::render_inbox_index_html(&pending)`.
  Previously it returned a bare `"elicitate inbox daemon — N pending"`
  text sentence.
- Daemon's `Route::Answer` (POST) now renders the answer
  confirmation page from `views::render_answer_html(&req, &values)`
  instead of an inline fragment.

### Fixed
- v0.5.1's `inbox --open` no longer needs to know the bound port:
  the inbox HTML pages link to themselves with the daemon's actual
  bind address via the `inbox_live_url()` helper.

## [0.5.2] — 2026-07-22

### Added
- **InboxChangeBus** (`inbox::change`) — process-wide bus that tracks a
  monotonic generation counter and broadcasts to all subscribers via
  `crossbeam-channel`. Auto-initialized on first mutation. `enqueue()`
  and `finalize()` call `bus::notify()` after their atomic rename.
- **InboxWatcher** — lightweight blocking subscriber that calls
  `wait_changed(timeout)` and returns an `Option<u64>` generation
  whenever the inbox dir mutates. Powers the TUI `--follow` mode.
- **`elicitate inbox --tui --follow`** — replaces the 1-second wall-clock
  poll with a blocking wait on InboxChangeBus. Re-renders within
  ~3 ms of the inbox dir mutation (vs. up to 1,000 ms before).
  Machine: `watcher.wait_changed(1s)` → returns immediately when a
  write happens in `enqueue/finalize → atomic rename`. Falls back
  to the existing `--poll-ms` interval when the bus is not wired
  (no-daemon mode).
- **7 new change-bus unit tests** — `bus_forwards_notify`,
  `multiple_subscribers_all_get_notified`,
  `watcher_timed_out_when_no_notify`,
  `watcher_coalesces_burst_notifies`, `generation_never_decreases`,
  `bus_capacity_does_not_block`, `bus_is_send_sync`.
- **`crossbeam-channel 0.5.16`** as a direct dependency (already in the
  transitive tree via tokio + tao; zero additional compile cost).

### Changed
- `tui::run()` now accepts `follow: bool`. When true and the inbox dir
  is available, the TUI loop subscribes to `InboxChangeBus::global()`
  and blocks on `watcher.wait_changed(...)` between refresh cycles.
- `elicitate inbox --tui` gained `--follow` / `--no-follow` flag.
  Default: `--follow` (bus-powered polling). Pass `--no-follow` to
  restore the v0.5 fixed-interval behaviour.

### Tests
- Total: **103 lib unit + 13 bin unit + 14 cli integration + 6 lib
  integration + 4 mcp stdio = 140 tests** (up from 133).

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
