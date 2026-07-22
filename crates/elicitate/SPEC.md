# elicitate — Specification

## 1. Problem

AI agents frequently stall because they need a single human decision and the only way to ask is via the
chat pane. Chat is the wrong surface: it interrupts flow, the answer mixes with prior context, and
the agent has to scrape free text to recover a structured value. We need a way for an agent to pop a
single, structured, modal decision onto the operator's desktop — quickly, with a guaranteed timeout,
in the same shape every time.

## 2. Goals

- **One popup, one decision.** The shape is a single field, an optional notes box, and Confirm/Cancel.
- **Same shape everywhere.** macOS and Windows renderers produce visually equivalent dialogs.
- **Sub-second to first paint** on a warm start. The agent should not stall perceptibly.
- **Bounded by `timeout_secs`.** No prompt can hang the agent.
- **Headless-safe.** When the platform has no display, fall back to a TUI that accepts the same
  inputs and emits the same JSON output. When CI runs, the JSON renderer returns a deterministic stub.
- **Secret-aware.** A field can be marked `secret: true`; the renderer must mask input and never log
  the value.
- **Plugin-friendly.** Expose the same surface as a Rust library, a CLI, an MCP server, and a skill
  manifest so any host agent can consume it.
- **Non-blocking.** When the agent can't or shouldn't wait for the popup, it queues the request in
  a durable inbox. The user answers later from the desktop, browser, phone (via iMessage / email
  deep link), or a different shell. The wait call returns as soon as any of them responds.

## 3. Non-goals

- Multi-page wizards. (Chain `elicit()` calls at the caller.)
- Free-form chat.
- Asynchronous / multi-user flows in the same prompt. (One popup, one operator.)
- Browser-based rendering for the *initial* prompt. We deliberately use the host OS's native
  controls so the prompt feels like a system dialog, not a webpage. (The async inbox *does* render
  the form in a browser when the user opts in — that's the trade-off for the non-blocking case.)
- Inbound IMAP/SMS parsing. Notification channels are one-way out; the response always comes back
  through the local inbox surface (browser form or CLI `answer`).

## 4. Surface area

### 4.1 Library — `elicitate::*`

```rust
pub enum FieldSpec { Boolean, Text, Choice, MultiSelect, Integer, Number, DateTime }
pub struct PromptSpec { title, question, field, notes?, buttons?, urgency, timeout_secs, request_id? }
pub enum ElicitResponse { Answered { value, notes? }, Cancelled { notes? }, TimedOut { elapsed_secs }, Failed { reason } }
pub enum Urgency { Info, Warning, Danger, Secret }
pub enum FieldValue { Boolean, Text, Choice, MultiSelect, Integer, Number, DateTime, Empty }

pub fn elicit(spec: &PromptSpec, opts: ElicitOptions) -> Result<ElicitResponse>;
pub fn schema_json() -> serde_json::Value;
```

### 4.2 CLI — `elicitate`

```
elicitate ask             # open a popup (blocking) or queue it with --async
elicitate ask --async     # enqueue and return open_url + request_id instantly
elicitate wait            # poll for the answer to a previously queued request
elicitate answer          # submit an answer to a queued request (scriptable)
elicitate inbox           # list / show / open / clean the inbox
elicitate daemon          # run the long-lived HTTP + tray + notifier server
elicitate install         # one-shot setup: copies binaries, writes PATH, registers launch agent
elicitate uninstall       # remove everything `install` added
elicitate validate        # validate a JSON spec without rendering
elicitate schema          # print JSON Schema
elicitate detect          # print platform + renderer info
elicitate version
elicitate smoke           # smoke-test the binary
elicitate serve           # explicit error: tells you to use `elicitate-mcp` instead
```

### 4.3 MCP — `elicitate-mcp`

JSON-RPC 2.0 over stdio. One tool, `elicitate_mcp`. Input is `PromptSpec`. Output is `ElicitResponse`.

### 4.4 Skill — `.elicitate/skills/elicitate/SKILL.md`

Universal skill manifest: describes when the agent should invoke the tool, what shape it must build,
and how to interpret the response.

### 4.5 Plugins

| Plugin       | Manifest                  | Install script |
| ------------ | ------------------------- | -------------- |
| Forgecode    | `plugin.toml`             | `install.sh`   |
| Codex        | `codex.toml`              | `install.sh`   |
| Cursor       | `cursor-mcp.json`         | `install.sh`   |

## 5. PromptSpec

```json
{
  "title": "string (≤ 120 chars)",
  "question": "string (≤ 1024 chars, may be empty)",
  "field": { "kind": "boolean", ... },
  "notes": { "label": "string", "default": "...", "max_length": 4096, "required": false },
  "buttons": { "cancel": "Cancel", "confirm": "OK", "default_is_cancel": false },
  "urgency": "info | warning | danger | secret",
  "timeout_secs": 60,
  "request_id": "opaque string (optional)"
}
```

`field` is a tagged union. Variants:

| Kind          | Extra                                                                 |
| ------------- | --------------------------------------------------------------------- |
| `boolean`     | `default: bool?`                                                      |
| `text`        | `default?: string`, `placeholder?: string`, `pattern?: string (regex)`, `max_length?: usize`, `multiline?: bool`, `secret?: bool` |
| `choice`      | `options: [{value, label, description?}]`, `default_index?: int`      |
| `multiselect` | same as `choice`, `min_selected?`, `max_selected?`                    |
| `integer`     | `min?: i64`, `max?: i64`, `default?: i64`                             |
| `number`      | `min?: f64`, `max?: f64`, `default?: f64`                             |
| `datetime`    | `kind: "date" | "time" | "datetime"`, `default?: ISO-8601`             |

## 6. Response

```json
{
  "status": "answered | cancelled | timed_out | failed",
  "value": { ... },        // present when status == answered
  "notes": "string",        // present when status ∈ {answered, cancelled}
  "elapsed_secs": 1.4,      // present when status == timed_out
  "reason": "string"        // present when status == failed
}
```

For `--async`, `elicitate ask` returns a different envelope:

```json
{
  "status": "queued",
  "request_id": "uuid-v4",
  "open_url": "http://127.0.0.1:7117/inbox/<id>",
  "path": "/Users/me/.elicitate/inbox/<id>.json",
  "channels": ["tray", "browser", "imessage", "email"]
}
```

## 7. Renderer selection

`render.rs::dispatch` chooses a renderer based on `ElicitOptions::renderer`:

1. `Auto` (default): detect platform → if GUI-eligible → `macos`/`windows`/`linux`; else `tty`.
2. `Gui` / `Macos` / `Windows` / `Linux`: force the chosen renderer, error if unavailable.
3. `Tty`: always `inquire`.
4. `Json`: deterministic stub used by CI tests; returns `TimedOut` after 0 ms.

The dispatch never panics. If a GUI renderer is unavailable, it returns a structured error
(`ElicitError::RendererUnavailable`) and the caller can decide to retry with `Tty`.

## 8. Concurrency model

The MCP server uses `tokio`. Each `elicitate_mcp` call runs in its own task with a `tokio::time::timeout`
wrapper. The render call itself runs on a dedicated blocking thread (renderer is synchronous,
sometimes must be on the main thread on macOS). The blocking thread is fed a crossbeam channel that
the timeout task signals with `Timeout` when the deadline fires.

## 9. Security & privacy

- **Secret fields.** `secret: true` switches to `NSSecureTextField` / `ES_PASSWORD`. The value is
  dropped after rendering returns. It is never logged, never serialized to `tracing` events,
  never echoed to the parent process's stderr.
- **Process boundary.** On macOS, the GUI runs in the same process (AppKit requires this), but the
  wait happens on a `std::thread` with a `wait`-style future so the agent's tokio runtime is not
  blocked.
- **No external network calls.** The library has zero outbound network dependencies. `Cargo.toml`
  has no `reqwest`/`hyper`/`tonic`/`surf`.
- **No value leakage in errors.** Error messages never include the prompt's content.

## 10. Async inbox

The async inbox is the non-blocking sibling of the blocking popup. It exists
because some flows simply cannot wait for the user to be at the keyboard:

- long-running agents that must keep working while the operator is in a
  meeting / on a phone / asleep,
- CI runs that surface a "what should we do about this flaky test?" prompt
  to a human channel,
- multi-agent setups where one agent delegates the decision to a human via
  a peer agent that itself is running unattended.

### 10.1 Lifecycle

```
                            enqueue        ┌── tray click ───┐
  ask --async ─────────────────────────► inbox/<id>.json ◀──┐
  (returns immediately)                   pending        │
                                                     answer ──▶ POST /answer/<id>
                                                                   │
                                              ◀─── inbox/<id>.json (renamed, atomic)
                                              answered
                                                                   │
  wait ──────────────────────────── polls file with backoff ────────┘
  (returns when file state changes)
```

The inbox directory (`~/.elicitate/inbox/` by default) is the durable store.
`enqueue` writes a single `PendingRequest` JSON; `submit_answer` does an
atomic rename to `Answered` / `Cancelled` / `TimedOut`. The wait loop polls
with exponential backoff (50ms → 2s).

### 10.2 Transport matrix

| Channel     | Direction   | Trigger                                   | Surface                         |
| ----------- | ----------- | ----------------------------------------- | ------------------------------- |
| Tray menu   | notify + RX | pending request appears / daemon starts   | NSStatusItem / Shell_NotifyIcon |
| Browser     | notify + RX | `elicitate inbox --open` / iMessage link  | HTML form served by daemon      |
| iMessage     | notify       | `elicitate-inbox.toml` has SMS gateway    | Twilio / Messages.app deep link |
| Email       | notify       | `elicitate-inbox.toml` has SMTP relay     | Sendmail / SMTP relay           |
| Local shell | RX          | `elicitate answer --request-id …`         | CLI                             |

All notify channels are **one-way out**. The user always responds through
the browser form (or the CLI). This keeps the attack surface small — there
is no inbound IMAP / SMS parser to harden.

### 10.3 Daemon responsibilities

`elicitate daemon` runs as a user service (launchd on macOS, systemd on
Linux, registry Run-key on Windows) installed by `elicitate install`. It:

1. binds `127.0.0.1:7117` (or `--port`) and serves the inbox index + per-request HTML forms,
2. watches the inbox directory for new pending requests,
3. shows a tray notification with the request title and a "Open" action,
4. (optional) forwards the request to iMessage / email per the config file,
5. persists answered / cancelled responses to disk.

If the daemon dies, the inbox directory is still the source of truth. The
next daemon instance re-reads it on startup and re-notifies any request
older than `--retry-after` that hasn't been answered.

### 10.4 Install

`elicitate install` is a one-shot setup that:

1. copies `elicitate` and `elicitate-mcp` to `--prefix` (default
   `~/.local/bin` on Linux, `~/Library/Application Support/elicitate/bin`
   on macOS, `%LOCALAPPDATA%\elicitate\bin` on Windows),
2. adds that prefix to the user's PATH in `.zshrc` / `.bashrc`
   (or PowerShell profile on Windows),
3. installs the inbox daemon as a user service (launch agent / systemd
   unit / registry Run key),
4. runs `elicitate smoke` to verify the renderer works.

`elicitate install --no-launch-agent` skips step 3. `elicitate install
--skip-path` skips step 2. `elicitate uninstall --yes` reverses everything
without prompting.

## 11. Acceptance criteria

A reviewer should be able to:

1. `cargo build -p elicitate` and see binaries `elicitate` and `elicitate-mcp`.
2. Run `elicitate schema` and see valid JSON Schema.
3. Run `elicitate detect` and see the detected platform + renderer.
4. Run `elicitate ask --title T --question Q --field-kind boolean --field-label "?" --renderer tty`
   and observe a TUI prompt. Press Enter. Observe a JSON response on stdout.
5. Run the MCP server under `mcp-client` and see `elicitate_mcp` listed with the correct schema.
6. Run `cargo test -p elicitate` and see green.
7. Run `elicitate-mcp` and pipe in a `tools/call` request with an invalid `title`. See a structured
   error response.
8. Run `elicitate ask --async --title T --field-kind boolean` and see a `queued` JSON envelope
   within ~20ms. Verify `<inbox>/<id>.json` was created.
9. Run `elicitate inbox --list --inbox-dir <dir>` and see the pending request in the index.
10. Run `elicitate answer --request-id <id> --value true --inbox-dir <dir>` and observe the JSON
    file move to the answered state. Run `elicitate wait --request-id <id>` from another shell
    in parallel and confirm it returned the answered value.
11. Run `elicitate install --prefix /tmp/test --no-launch-agent --skip-path --no-smoke` and
    confirm both binaries are at `/tmp/test/{elicitate,elicitate-mcp}`. Run
    `elicitate uninstall --prefix /tmp/test --yes` and confirm they're gone.
12. Run `elicitate daemon --inbox-dir /tmp/test --port 0` (random port) and confirm it serves
    `GET /health` returning 200.
