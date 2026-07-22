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

## 3. Non-goals

- Multi-page wizards. (Chain `elicit()` calls at the caller.)
- Free-form chat.
- Asynchronous / multi-user flows. (One popup, one operator.)
- Browser-based rendering. We deliberately use the host OS's native controls so the prompt feels
  like a system dialog, not a webpage.

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
elicitate ask        # open a popup from flags or stdin
elicitate validate   # validate a JSON spec without rendering
elicitate schema     # print JSON Schema
elicitate detect     # print platform + renderer info
elicitate version
elicitate smoke      # smoke-test the binary
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

## 10. Acceptance criteria

A reviewer should be able to:

1. `cargo build -p elicitate` and see a binary `elicitate` and `elicitate-mcp`.
2. Run `elicitate schema` and see valid JSON Schema.
3. Run `elicitate detect` and see the detected platform + renderer.
4. Run `elicitate ask --title T --question Q --field-kind boolean --field-label "?" --renderer tty`
   and observe a TUI prompt. Press Enter. Observe a JSON response on stdout.
5. Run the MCP server under `mcp-client` and see `elicitate_mcp` listed with the correct schema.
6. Run `cargo test -p elicitate` and see green.
7. Run `elicitate-mcp` and pipe in a `tools/call` request with an invalid `title`. See a structured
   error response.
