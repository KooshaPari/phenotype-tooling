# elicitate

Native, agent-elicited prompts. One popup, one decision, back to the agent.

`elicitate` is an MCP tool, CLI, and Rust library that opens a **native OS popup window** so an AI agent can ask a human a structured question and wait for an answer. It is built for the moment an agent needs a missing decision, a missing secret, or a missing preference — and is fast enough (sub-second to first paint on a warm start) that the agent can stay in flow.

## What it does

The agent sends a JSON prompt describing one field (boolean, text, choice, integer, number, datetime, multiselect, file/path), an optional notes box, and an urgency. `elicitate` opens a small native dialog on the operator's desktop — the **exact same shape on macOS and Windows** — and blocks until the human answers, cancels, or the timeout fires. The result is returned as a structured JSON `ElicitResponse`.

It is **not** a chat UI. It is a single decision. Like `InputBox` from Visual Basic, but with a schema, a timeout, and secrets.

## Surface area

| Form             | Path                                                                |
| ---------------- | ------------------------------------------------------------------- |
| Rust library     | `elicitate::spec::*`, `elicitate::elicit()`, `elicitate::schema_json()` |
| CLI              | `elicitate ask --from-json '{...}'`                                 |
| MCP server (stdio) | `elicitate-mcp`                                                    |
| Skill            | `.elicitate/skills/elicitate/SKILL.md`                              |
| Plugin — Forgecode | `plugins/forgecode/plugin.toml`                                   |
| Plugin — Codex   | `plugins/codex/codex.toml`                                          |
| Plugin — Cursor  | `plugins/cursor/cursor-mcp.json`                                    |

## Quickstart

### As a library

```rust
use elicitate::{elicit, ElicitOptions, RendererPreference};
use elicitate::spec::*;

let spec = PromptSpec {
    title: "Rename 23 identifiers".into(),
    question: "I'll rename identifiers across 8 files. Proceed?".into(),
    field: FieldSpec::Boolean { label: "Proceed?".into(), default: Some(true) },
    notes: None,
    buttons: None,
    urgency: Urgency::Info,
    timeout_secs: 120,
    request_id: None,
};

let response = elicit(&spec, ElicitOptions {
    renderer: RendererPreference::AutoGui,
    ..Default::default()
})?;

match response {
    ElicitResponse::Answered { value, notes } => { /* use it */ }
    ElicitResponse::Cancelled { .. } => { /* user said no */ }
    ElicitResponse::TimedOut { .. } => { /* no answer */ }
    ElicitResponse::Failed { reason } => { /* surface to caller */ }
}
```

### As a CLI

```bash
# Open a popup with a literal JSON spec
elicitate ask --title "Deploy?" --question "Deploy to production?" \
    --field-kind boolean --field-label "Confirm" --field-default true

# Pipe a JSON spec via stdin
echo '{"title":"OK?","question":"","field":{"kind":"boolean","label":"OK","default":true}}' \
  | elicitate ask --from-json -

# Validate a spec without rendering
elicitate validate --from-file spec.json

# Print JSON Schema
elicitate schema
```

### As an MCP server

Add to `mcp_servers.json`:

```json
{
  "mcpServers": {
    "elicitate": {
      "command": "elicitate-mcp",
      "args": [],
      "transport": "stdio"
    }
  }
}
```

The server exposes a single tool, `elicitate_mcp`. It takes the same shape as `PromptSpec` and returns the same shape as `ElicitResponse`.

## Platform support

| OS      | Renderer         | Backend                                                                 |
| ------- | ---------------- | ----------------------------------------------------------------------- |
| macOS   | Native NSPanel   | AppKit via `objc2` + `cocoa` — modal sheet attached to the active app, async dispatch queue for the run-loop, lands on macOS 11+ |
| Windows | Native Win32     | `CreateWindowExW` + standard controls, `CoTaskMemFree` for COM strings, modal via `EnableWindow` on the owner, lands on Windows 10 1809+ |
| Linux   | GTK4 or TUI      | GTK4 dialog with the same layout, or fall back to the TUI renderer (`inquire`) |
| Headless | TUI / JSON     | `inquire`-based terminal UI; machine-readable `{}` on `--renderer json` |

If `elicitate` cannot show a GUI (no display, SSH session, sandbox without entitlements), it **automatically falls back** to the TUI. This is observable: run `elicitate detect` to see which path it took.

## Plugin compatibility

| Client     | Integration                                                                                                                                       |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Forgecode  | `plugins/forgecode/plugin.toml` declares the tool; the dispatcher wraps it for the agent; `install.sh` installs the CLI and registers the skill |
| Codex      | `plugins/codex/codex.toml` registers the MCP server with the canonical transport; `install.sh` writes `~/.codex/mcp.toml`                       |
| Cursor     | `plugins/cursor/cursor-mcp.json` is the standard Cursor MCP manifest; `install.sh` merges into `~/.cursor/mcp.json`                              |

## Architecture

```
                ┌──────────────────┐
                │ Agent (any host) │
                └────────┬─────────┘
                         │ JSON-RPC over stdio
                         ▼
              ┌─────────────────────────┐
              │ elicitate-mcp (rmcp)    │
              │ validates spec, then   │
              │ dispatches              │
              └────────┬────────────────┘
                       │
                       ▼
              ┌─────────────────────────┐
              │ elicitate library       │
              │   platform/detect.rs    │──── chooses renderer
              │   render.rs             │
              │   platform/{mac,win,    │
              │     linux,tty}.rs       │
              └────────┬────────────────┘
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
   ┌─────────────────┐   ┌─────────────────┐
   │ Native GUI      │   │ TUI fallback    │
   │ (AppKit / Win32)│   │ (inquire)       │
   └─────────────────┘   └─────────────────┘
```

The single source of truth for the prompt and response shape is `elicitate::spec`. The CLI, the MCP server, the GUI, and the TUI all consume it.

## Safety properties

- **Process isolation.** The GUI process is launched as a separate detached process so the agent's event loop is never blocked by Cocoa/UIKit. The parent waits with `waitpid` and a wall-clock timer.
- **Bounded wait.** Every render path is bounded by `timeout_secs`. On timeout, the GUI is dismissed, the result is `TimedOut`, and the parent's deadline is honored.
- **Secret-aware rendering.** Fields with `secret: true` use `NSSecureTextField` on macOS and `ES_PASSWORD` on Windows. The value is never logged.
- **No value leakage.** `tracing` events at INFO level show only the request id and the status (Answered/Cancelled/TimedOut), never the value.

## License

MIT OR Apache-2.0 (dual-licensed, matching the rest of `phenotype-tooling`).
