# elicitate — Research Document

> **Date:** 2026-07-21
> **Owner:** @KooshaPari
> **Status:** READY-FOR-IMPLEMENTATION
> **Crate path:** `phenotype-tooling/crates/elicitate/`
> **Binary name:** `elicitate` (long-form `elicitate-mcp` for the MCP server mode)
> **Tier:** 2 (extension; UX/AX-facing)
> **Maturity target:** stable

---

## 1. Executive summary

`elicitate` is a Rust-native elicitation tool that lets an autonomous agent
(Forge / Codex / Cursor / Claude Code / anything MCP-compatible) pause mid-task,
present the human user with a **native OS popup** containing a form field (the
"agent-devised" prompt) plus an optional notes/free-text box, and synchronously
receive the human's answer back as a typed JSON response.

It ships **four** coordinated surfaces:

| Surface | Path | Format | Purpose |
|---|---|---|---|
| **Rust library** | `src/lib.rs` | Rust crate | Reusable core (schema, dialog, transports) |
| **CLI binary** | `src/main.rs` | clap subcommand | `elicitate ask`, `elicitate schema`, `elicitate serve` |
| **MCP server** | `src/mcp.rs` | stdio JSON-RPC | `elicitate_mcp` tool exposed to forgecode/codex/cursor |
| **Skill + Plugins** | `.elicitate/skills/elicitate/SKILL.md` + `plugins/{forgecode,codex,cursor}/*` | Markdown manifest | Pre-wired tool registration for each host agent |
| **Skill** | `.elicitate/skills/elicitate/` | SKILL.md frontmatter | Agent-readable description of the tool |

The crucial design choice: **the popup is rendered by the OS, not by a
webview**. On macOS the dialog uses `osascript` driving `display dialog`
(native NSAlert under the hood). On Windows it uses PowerShell driving
`Add-Type -AssemblyName System.Windows.Forms` (true Win32 form). Both run
**out-of-process** so the MCP server is never blocked on UI thread, and both
are **modal at the OS layer** (the human cannot ignore them) but **non-blocking
for the agent's other tool calls** thanks to a request-id correlation layer
that multiplexes multiple in-flight elicitation requests.

## 2. Problem statement

Autonomous agents routinely hit decision points where guessing is worse than
asking. Examples that came up repeatedly in fleet telemetry (per
`worklogs/RESEARCH.md` §3):

- "I have two valid approaches — proceed with A or B?"
- "Should I commit with this message or amend?"
- "Enter the secret value the next tool needs"
- "Approve this PR description?"
- "Pick the deployment target (staging|prod|canary)?"

Today the agent either (a) guesses, (b) dumps a wall-of-text question into
the terminal and hopes the human sees it, or (c) requires the human to
hand-type JSON into a chat reply. All three are bad AX. None are blocking
modal UI that **demands** a response.

We need a primitive that:

1. Is **modal** (the human cannot miss it; the agent cannot proceed without
   an answer or explicit cancel).
2. Runs on **native OS chrome** (no electron, no webview) so the popup feels
   like every other system dialog and survives terminal multiplexer state.
3. Has a **typed schema** the agent authors (field label, input type,
   validation, optional notes/free-text box) — not free-form "ask a question
   in plain English and pray the parser interprets it".
4. Works **identically** from Forge, Codex, Cursor, Claude Code, or any
   stdio MCP client — same UX surface regardless of host.
5. Is **non-blocking for concurrent tool calls** so a long-running agent
   session doesn't deadlock when two prompts are queued.
6. Returns a **structured JSON answer** the agent can `match` on
   (`Cancelled` | `Declined` | `Answered { value, notes }`).
7. Defaults to a **TTY fallback** (`inquire` crate) when no GUI is available
   (SSH session, headless CI, Linux without X).

## 3. Why a native popup (vs. TUI / webview / Slack / etc.)

| Approach | Pros | Cons | Verdict |
|---|---|---|---|
| Native NSAlert (macOS) / Win32 Form (Windows) | Modal, OS-styled, always-on-top, accessible, screenshot-friendly, screen-reader-friendly | OS-specific code paths | ✅ **chosen** |
| TUI dialog (`inquire`/`dialoguer`) | Cross-platform, zero deps | Not modal at OS layer; invisible if terminal is backgrounded; no accessibility | ❌ fallback only |
| Electron webview | Cross-platform, full styling | 50MB+ binary, slow startup, NOT modal at OS layer, security surface | ❌ overkill, wrong tool |
| Slack/Discord notification | Async, persists | Not blocking; human may not see; requires bot setup | ❌ wrong primitive |
| HTTP form in browser tab | Familiar UX | Backgrounded, not modal, requires browser; clutters tabs | ❌ |
| AppleScript only (`osascript -e 'display dialog'`) | Tiny, zero deps, modal | macOS only | ✅ on macOS |
| PowerShell `System.Windows.Forms` | Modal, accessible, Win32-native | Windows only | ✅ on Windows |

We use **OS-native APIs via the most-available scripting shell** on each
platform (AppleScript on macOS, PowerShell on Windows, `zenity`/`kdialog` on
Linux). The agent never sees the platform split — the `elicitate` library
detects platform at runtime and picks the right renderer. The agent always
sees the same `ElicitResponse` enum.

## 4. Platform-native popup mechanics

### 4.1 macOS — `osascript` + `display dialog`

AppleScript's `display dialog` command is a thin wrapper over `NSAlert`
(AppKit). Key properties:

- **Modal at the OS layer**: the dialog window owns input focus; the
  spawning process can be backgrounded without losing the dialog.
- **Blocks until user responds**: `osascript` does not return until the user
  clicks a button. This is the blocking property we exploit — the spawned
  subprocess (an `elicitate-popup-mac` shim) writes the user's response to
  stdout and exits with code 0 (accepted) or 1 (cancelled).
- **Supports a default text field** and **optional text** (multi-line
  hidden behind "Show details" disclosure triangle — perfect for the
  "notes" box).
- **Supports `as critical`**: makes the dialog appear on top of all
  windows and play an alert sound.
- **Supports `with title` and `with icon`** for branding.

The Rust side:

```rust
// crates/elicitate/src/platform/macos.rs
use std::process::Command;

pub fn render(prompt: &PromptSpec) -> Result<ElicitResponse> {
    let script = build_applescript(prompt);
    let out = Command::new("osascript")
        .arg("-e").arg(script)
        .output()?;
    parse_applescript_output(&out.stdout, &out.stderr)
}
```

Where `build_applescript` produces something like:

```applescript
set theResponse to display dialog "
    Title: Approve deployment plan?
    Question: The diff touches 14 files. Continue with rollout?

    Field: confirmation_token
    Default: yes
    Secret: false
" with title "elicitate · approval requested" default answer "yes" \
  with icon caution \
  buttons {"Cancel", "OK"} default button "OK" \
  giving up after 600

set theField to text returned of theResponse
set theNotes to (if button returned of theResponse is "OK") then "" else ""
return theField & "|" & theNotes
```

Notes on the macOS design:

- We **escape all string interpolation** through `shell_escape`-style quoting
  to prevent AppleScript injection from the agent's authored prompt.
- The default timeout is **10 minutes** (`giving up after 600`). Agents
  should never wait longer than that — if they do, they get a `TimedOut`
  response. The timeout is configurable via `--timeout-secs`.
- The dialog is spawned in a **separate process tree** via `setsid` so a
  SIGTERM to the MCP server doesn't kill the dialog.

### 4.2 Windows — PowerShell + Win32 Form

PowerShell on Windows can instantiate `System.Windows.Forms.Form` (a
managed wrapper over `USER32.dll`'s `CreateWindowEx`). The popup:

- Is **modal at the Win32 layer** (`Form.ShowDialog()` blocks the calling
  thread; we spawn a PowerShell child process so the MCP server is not
  blocked).
- Has a **textbox** for the field (single-line `TextBox` or multi-line
  `RichTextBox` depending on `notes_required`).
- Supports a **default value**, **placeholder text**, **max length**, and
  **input mask** (`PasswordChar = '*'` for secrets).
- Returns the entered value via `Write-Output` so the Rust parent can
  read it from stdout.
- Honors the **Cancel button** (the form's `DialogResult = DialogResult.Cancel`).

The Rust side:

```rust
// crates/elicitate/src/platform/windows.rs
use std::process::Command;

pub fn render(prompt: &PromptSpec) -> Result<ElicitResponse> {
    let script = build_powershell(prompt);
    let out = Command::new("powershell.exe")
        .arg("-NoProfile")
        .arg("-NonInteractive")
        .arg("-Command").arg(script)
        .output()?;
    parse_powershell_output(&out.stdout, &out.stderr)
}
```

Where `build_powershell` produces a 30-line script that:

1. Loads `System.Windows.Forms` and `System.Drawing` assemblies.
2. Constructs a `Form` with title, icon, and `TopMost = $true`.
3. Adds a `Label` for the question, a `TextBox` for the field (with
   `PasswordChar` if secret), and a `RichTextBox` for notes (if enabled).
4. Adds `OK` / `Cancel` buttons wired to set `$script:dialogResult`.
5. Calls `$form.ShowDialog()` (blocks the PowerShell process).
6. Prints `$dialogResult` + field value + notes to stdout as
   `STATUS|VALUE|NOTES` for easy parsing.

### 4.3 Linux — `zenity` / `kdialog` / TUI fallback

Linux GUI dialogs are non-portable across distros. We use a priority chain:

1. `zenity --entry --text=...` (GNOME; widely packaged)
2. `kdialog --inputbox ...` (KDE)
3. `python3 -c "import tkinter; ..."` (Tk; almost always present)
4. **`inquire` crate TUI** (last resort; what runs in CI/headless)

The TUI fallback is the only renderer we ship a Rust dependency for
(`inquire = "0.7"`). All other platforms shell out to the OS tool.

### 4.4 SSH / headless detection

Before rendering, we check:

- `$DISPLAY` (X11) and `$WAYLAND_DISPLAY` (Wayland) — both unset → headless
- `$SSH_CLIENT` or `$SSH_TTY` set → SSH session (default to TUI unless
  `--allow-gui-over-ssh` is set; some users forward X11 over SSH)
- `cargo test` / `CI=true` env → TUI only
- `--renderer=force-tty` / `--renderer=force-gui` → override

The detection lives in `src/platform/select.rs` and is unit-testable.

## 5. The schema: `PromptSpec`

The agent authors the dialog. The schema is the contract.

```rust
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct PromptSpec {
    /// One-line title shown in the popup title bar / window header.
    /// Examples: "Approve deployment?", "Provide API key", "Pick a target"
    /// Max 80 chars.
    pub title: String,

    /// Multi-line body explaining context. Rendered as the question label
    /// above the input field. Markdown is NOT rendered — plain text only
    /// (popup native chrome has no markdown renderer; we deliberately
    /// don't ship a webview). Max 2000 chars.
    pub question: String,

    /// The input field configuration.
    pub field: FieldSpec,

    /// Whether to show the notes/free-text box.
    /// Default: false (single-field dialog).
    #[serde(default)]
    pub notes: Option<NotesSpec>,

    /// Button labels. Default: ["Cancel", "OK"].
    #[serde(default)]
    pub buttons: Option<ButtonSpec>,

    /// Urgency hint — affects icon + sound.
    /// - "info"    : NSAlertStyleInformational / MB_ICONINFORMATION
    /// - "warning" : NSAlertStyleWarning        / MB_ICONWARNING
    /// - "error"   : NSAlertStyleCritical       / MB_ICONERROR
    /// - "secret"  : same as warning + mask input
    #[serde(default = "default_urgency")]
    pub urgency: Urgency,

    /// Timeout in seconds. After this, response is `TimedOut`.
    /// Default: 600 (10 min). Set to 0 for no timeout (CI/automation only).
    #[serde(default = "default_timeout_secs")]
    pub timeout_secs: u32,

    /// Request ID for correlation when multiple prompts are queued.
    /// If omitted, the library auto-generates a UUIDv4.
    #[serde(default)]
    pub request_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum FieldSpec {
    /// Single-line text input.
    Text {
        label: String,
        default: Option<String>,
        placeholder: Option<String>,
        max_length: Option<u32>,
        /// If true, render as password field (••• mask).
        secret: bool,
        /// Regex the value must match before OK is enabled.
        /// Stored as string; compiled at runtime with the `regex` crate.
        pattern: Option<String>,
    },
    /// Long-form multi-line text.
    LongText {
        label: String,
        default: Option<String>,
        max_length: Option<u32>,
    },
    /// Integer in [min, max].
    Integer {
        label: String,
        min: Option<i64>,
        max: Option<i64>,
        default: Option<i64>,
    },
    /// Choice from a fixed list (rendered as radio buttons on GUI,
    /// as a select prompt on TUI).
    Choice {
        label: String,
        options: Vec<ChoiceOption>,
        default_index: Option<usize>,
    },
    /// Boolean yes/no. Renders as 2 buttons.
    Boolean {
        label: String,
        default: Option<bool>,
    },
    /// Date / time picker.
    DateTime {
        label: String,
        default: Option<String>, // RFC3339
        kind: DateTimeKind,      // Date | Time | DateTime
    },
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ChoiceOption {
    pub value: String,
    pub label: String,
    #[serde(default)]
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct NotesSpec {
    pub label: String,                  // "Why did you choose this?"
    pub default: Option<String>,
    pub max_length: Option<u32>,
    pub required: bool,                 // blocks OK until notes non-empty
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ButtonSpec {
    pub cancel: String,                 // default: "Cancel"
    pub confirm: String,                // default: "OK"
    /// If true, swap which button is the default (Enter-key target).
    #[serde(default)]
    pub default_is_cancel: bool,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, JsonSchema, Default)]
#[serde(rename_all = "lowercase")]
pub enum Urgency { #[default] Info, Warning, Error, Secret }

#[derive(Debug, Clone, Copy, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "lowercase")]
pub enum DateTimeKind { Date, Time, DateTime }
```

The `ElicitResponse`:

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "status", rename_all = "snake_case")]
pub enum ElicitResponse {
    /// User clicked OK and entered a value.
    Answered { value: FieldValue, notes: Option<String> },
    /// User clicked Cancel. Notes may be populated if they typed some.
    Cancelled { notes: Option<String> },
    /// Popup timed out (--timeout-secs reached with no response).
    TimedOut { elapsed_secs: f64 },
    /// Popup failed to render (e.g., no display, osascript missing).
    /// The agent should fall back to a different strategy.
    Failed { reason: String },
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
#[serde(tag = "kind", content = "value", rename_all = "snake_case")]
pub enum FieldValue {
    Text(String),
    LongText(String),
    Integer(i64),
    Choice { value: String, index: usize },
    Boolean(bool),
    DateTime(String), // RFC3339
}
```

## 6. The four surfaces

### 6.1 Library (`crates/elicitate/src/lib.rs`)

Public API:

```rust
pub fn elicit(spec: &PromptSpec) -> Result<ElicitResponse, ElicitError>;
pub async fn elicit_async(spec: &PromptSpec) -> Result<ElicitResponse, ElicitError>;
pub fn elicit_with(spec: &PromptSpec, opts: &ElicitOptions) -> Result<ElicitResponse, ElicitError>;
pub fn schema_json() -> serde_json::Value;       // returns PromptSpec JSON Schema
pub fn platform() -> Platform;                    // for diagnostics
pub fn detect_renderer() -> RendererKind;         // for --renderer override
```

The library is sync-first (popup UI is fundamentally synchronous from the
caller's POV — the agent is waiting), with an async wrapper that uses
`tokio::task::spawn_blocking` so the async runtime isn't blocked.

`ElicitOptions` lets the caller override defaults:

```rust
pub struct ElicitOptions {
    pub renderer: RendererPreference,  // AutoGui | ForceGui | ForceTty
    pub timeout: Option<Duration>,
    pub working_dir: Option<PathBuf>,  // for resolving icons
    pub parent_pid: Option<u32>,       // for focus stealing
}
```

### 6.2 CLI binary (`elicitate ask ...`)

```
elicitate ask --title "Approve deployment?" \
              --question "The diff touches 14 files..." \
              --field-text label="Are you sure?" default=yes \
              --notes label="Why?" \
              --urgency warning \
              --timeout-secs 60

elicitate schema               # print PromptSpec JSON Schema
elicitate schema --field       # print just FieldSpec schema
elicitate detect               # print detected platform + renderer
elicitate serve                # run MCP server on stdio
elicitate render --from-json '{"title":"..."}'   # for shell scripting
elicitate render --from-file ./prompt.json
elicitate smoke                # render a test popup and exit
elicitate version
```

The CLI is what `elicitate-mcp` (the MCP server binary) shells out to
under the hood. This separation lets the popup renderer be tested
independently and lets shell scripts use the same primitive.

### 6.3 MCP server (`src/mcp.rs`)

Single tool: `elicitate_mcp`.

```json
{
  "name": "elicitate_mcp",
  "description": "Pause and ask the human user a structured question via a native OS popup. ...",
  "inputSchema": { "$ref": "#/schemas/PromptSpec" },
  "outputSchema": { "$ref": "#/schemas/ElicitResponse" }
}
```

Wire format: standard MCP stdio JSON-RPC 2.0. Server uses `rmcp` crate
(v0.2 — the rust-sdk for MCP).

The MCP server is a **single tool by design**: every question the agent
wants to ask goes through `elicitate_mcp`. The agent composes the
`PromptSpec` to express exactly what UI it wants. This keeps the MCP
surface tiny (one tool, one schema) while supporting infinite UX variation
through schema composition.

Concurrent requests: the server maintains a `HashMap<RequestId,
oneshot::Sender<ElicitResponse>>`. When two prompts are queued, both
popups are displayed (the user sees them stacked); each popup's response
is routed back to its corresponding request. The MCP server never blocks
on a single request — `tokio::spawn` per request, `await` on the oneshot.

### 6.4 Skills + Plugins

#### Skill: `.elicitate/skills/elicitate/SKILL.md`

The skill follows the SKILL.md frontmatter convention used by Forge
and Claude Code:

```markdown
---
name: elicitate
description: Pause and ask the human user a structured question via a native OS popup. Use whenever you need user input to disambiguate, confirm, collect a secret, or pick among options.
version: 0.1.0
license: MIT
---

# elicitate

Renders a modal native OS dialog (NSAlert on macOS, Win32 Form on
Windows, zenity/Tk/inquire on Linux) and returns the user's answer as
typed JSON.

## When to invoke

- You face 2+ equally valid next steps and guessing is worse than asking.
- The next tool requires a secret or token you don't have.
- The user must approve a destructive / external action (push, deploy,
  publish, send).
- You need to confirm a generated artifact (commit message, PR body,
  release notes).

## Schema

[Full PromptSpec embedded as YAML, then prose walk-through]

## Response shape

[Full ElicitResponse enum documented]

## Examples

### Ask yes/no

[example]

### Ask for a secret

[example with urgency=secret, field.kind=text secret=true]

### Ask for a multi-choice with required notes

[example with field.kind=choice + notes.required=true]

## Anti-patterns

- Don't ask questions you can answer yourself by reading the codebase.
- Don't ask questions whose answers are deterministic from context.
- Don't ask "shall I proceed?" after a non-destructive read.
```

The skill file is **identical across all three host agents** (Forge,
Codex, Cursor) — they all consume the same SKILL.md format. Host-specific
configuration lives in the `plugins/<host>/` directories.

#### Plugins

```
crates/elicitate/plugins/
├── forgecode/
│   ├── plugin.toml          # Forge plugin manifest
│   ├── install.sh           # one-line installer
│   └── README.md
├── codex/
│   ├── codex.toml           # Codex MCP config snippet
│   ├── install.sh
│   └── README.md
└── cursor/
    ├── cursor-mcp.json      # Cursor MCP config snippet
    ├── install.sh
    └── README.md
```

**Forge** (`plugins/forgecode/plugin.toml`):

```toml
[plugin]
name = "elicitate"
version = "0.1.0"
description = "Native OS popup elicitation tool"
author = "Phenotype Contributors"
license = "MIT"

[skill]
path = "../../.elicitate/skills/elicitate/SKILL.md"
auto_load = true

[[mcp_servers]]
name = "elicitate_mcp"
command = "elicitate-mcp"
args = ["serve"]
transport = "stdio"
```

**Codex** (`plugins/codex/codex.toml`):

```toml
[mcp_servers.elicitate_mcp]
command = "elicitate-mcp"
args = ["serve"]
disabled = false

[skills.elicitate]
path = ".elicitate/skills/elicitate/SKILL.md"
auto_activate = true
```

**Cursor** (`plugins/cursor/cursor-mcp.json`):

```json
{
  "mcpServers": {
    "elicitate_mcp": {
      "command": "elicitate-mcp",
      "args": ["serve"],
      "transport": "stdio"
    }
  }
}
```

The skill activation is handled by Cursor's "Project Rules" feature via
a generated `.cursorrules` snippet:

```
# elicitate
When the user or the agent needs structured input, prefer the
elicitate_mcp tool with a PromptSpec over inline questions.
```

## 7. Why these technologies

| Choice | Rationale | Alternatives considered |
|---|---|---|
| **Rust** | Phenotype scripting policy is Rust-first. Single binary per host. Zero runtime deps on macOS/Windows. | Python (slower startup, harder single-binary); Go (cross-compile pain for Win32 forms) |
| **`rmcp` 0.2** | Official Rust MCP SDK. Schema export built-in. Async-first. | `mcp-rs` (less maintained); hand-rolled JSON-RPC (regression risk) |
| **`clap` 4 derive** | Workspace convention. Used by 26+ existing crates. | `argh` (less discoverable), hand-rolled (regression risk) |
| **`serde` + `schemars`** | Workspace convention. JSON Schema derive is the cheapest path to MCP `inputSchema`. | `serde_json` alone (manual schema), `ts-rs` (no MCP benefit) |
| **`tokio`** | Workspace async runtime. | `async-std` (not used in workspace) |
| **AppleScript via `osascript`** | Already on every macOS install (system component since OS 8). No dep. | `objc`/`cocoa` crate (heavier, requires Xcode SDK linking, AppKit authorship friction) |
| **PowerShell `Add-Type System.Windows.Forms`** | On every Windows 10/11 / Server 2016+. No dep. | `winit`/`winapi` direct (Rust ABI fragility against Win32 patches), C# shim binary (extra build step) |
| **`inquire` for TUI fallback** | Workspace-aligned (used by `release-cut` ad-hoc). Clean terminal fallback. | `dialoguer` (less actively maintained) |
| **`regex` for pattern validation** | Workspace dep. | `fancy-regex` (overkill) |
| **`uuid` for request IDs** | Workspace dep. | `nanoid` (not in workspace) |
| **`chrono` for DateTime** | Workspace dep. | `time` (not in workspace) |
| **`thiserror` for error enums** | Workspace convention. | `anyhow` (less typed at API boundary) |
| **`tracing` for structured logs** | Workspace convention. | `log` (no spans) |

## 8. Concurrency model

The MCP server multiplexes multiple in-flight elicitation requests:

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP server (tokio)                        │
│                                                              │
│   JSON-RPC in  ──►  Router  ──►  HashMap<ReqId, oneshot>    │
│                                  │                           │
│                                  ▼                           │
│                            tokio::spawn                      │
│                                  │                           │
│                                  ▼                           │
│                          render_blocking                     │
│                          (osascript / powershell)            │
│                                  │                           │
│                                  ▼                           │
│                          response ──► oneshot.send()         │
│                                                              │
│   JSON-RPC out ◄── await oneshot                            │
└─────────────────────────────────────────────────────────────┘
```

Key invariants:

- One popup process per request. Two simultaneous requests = two popup
  processes. The OS handles window stacking (NSAlert queues modally on
  macOS; Win32 forms are top-most only by virtue of `TopMost = true`).
- Each popup process is detached (`setsid` on POSIX,
  `CREATE_NEW_PROCESS_GROUP` on Windows) so a SIGTERM to the server
  doesn't kill in-flight popups.
- The server exposes `/metrics` (when `observability` feature is enabled
  via the workspace's `phenotype-tooling-observability` crate) for
  monitoring: `elicitate_in_flight`, `elicitate_total`,
  `elicitate_timeouts_total`, `elicitate_failures_total`.
- All popups emit a structured `tracing` event on close with
  `{request_id, status, elapsed_ms, renderer, platform}`.

## 9. Security & privacy

- **Secrets are masked in the field** when `field.secret = true` (PowerShell
  `PasswordChar`, macOS NSSecureTextField via `display dialog` with the
  `default answer ""` + manual echo suppression).
- **Notes field is NOT masked** even when the field is secret — the
  popup explicitly warns in the body that notes are visible.
- **No popup content is logged at INFO level**. The library uses
  `tracing` with explicit field redaction:
  `tracing::info!(request_id, status, elapsed_ms, "popup closed")` —
  never includes the entered value.
- **The `secret` urgency** auto-applies `field.secret = true` if the agent
  forgets to set it. Defense-in-depth.
- **No telemetry leaves the host**. No HTTP. No analytics. The crate is
  100% local; the binary never makes an outbound network call.
- **Input is shell-escaped** before being interpolated into AppleScript
  or PowerShell to prevent injection from agent-authored prompts.

## 10. Failure modes (and how each is handled)

| Failure | Detection | Response | UX consequence |
|---|---|---|---|
| macOS, no `osascript` | `which osascript` fails | Fallback to TUI | User sees terminal prompt instead of popup |
| Windows, no PowerShell | `which powershell.exe` fails | Fallback to TUI | Same |
| Linux, no `zenity`/`kdialog`/`tkinter` | Probe each | Fallback to `inquire` TUI | Same |
| Headless (no `$DISPLAY`, no `$WAYLAND_DISPLAY`, no SSH X-forward) | Env probe | Force TUI | Same |
| User dismisses with X / Cmd+W / Escape | Button returned = Cancel | `Cancelled` | Agent gets a typed cancel |
| Timeout | `giving up after N` / `Form.Timer` | `TimedOut` | Agent gets typed timeout |
| AppleScript injection attempt in prompt | Shell-escape | `Failed { reason: "invalid prompt" }` | Agent retries with sanitized spec |
| Process spawn fails | `Command::status()` Err | `Failed { reason }` | Agent retries with `--renderer=force-tty` |
| MCP server gets SIGTERM mid-popup | Signal handler | Detach popup from process group; popup persists | Popup survives server restart |
| Two popups simultaneously | Request ID correlation | Both render; each response routed to correct request | User sees both, answers both |
| User types invalid value (fails regex) | Validation hook | OK button disabled until valid | Forced retry |

## 11. Test matrix

```
crates/elicitate/tests/
├── lib.rs                    # integration tests for the library
├── schema.rs                 # JSON Schema round-trip
├── platform_macos.rs         # macOS-specific (cfg-gated)
├── platform_windows.rs       # Windows-specific (cfg-gated)
├── platform_linux.rs         # Linux-specific (cfg-gated)
├── mcp_stdio.rs              # spawn MCP server, send tool call, assert response
├── cli.rs                    # spawn binary, assert exit codes + stdout JSON
└── fixtures/
    ├── simple_text.json      # PromptSpec fixtures for snapshot tests
    ├── choice_with_notes.json
    ├── secret.json
    └── timeout.json
```

`cargo test` runs everything that doesn't require a GUI. GUI tests are
`#[ignore]` by default and run via `cargo test -- --ignored` on CI hosts
with a display attached.

Snapshot tests lock the JSON Schema output — if we accidentally change
the schema, CI fails. This is the contract with every plugin/host.

## 12. FR (functional requirements) sketch

To be tracked in AgilePlus once approved. Sketch:

- **FR-ELIC-001**: Library exposes `elicit(spec) -> Result<ElicitResponse>`.
- **FR-ELIC-002**: CLI exposes `elicitate ask` with `--from-json`,
  `--from-file`, and flag equivalents.
- **FR-ELIC-003**: MCP server exposes exactly one tool, `elicitate_mcp`.
- **FR-ELIC-004**: macOS renderer uses `osascript` `display dialog`.
- **FR-ELIC-005**: Windows renderer uses PowerShell `System.Windows.Forms`.
- **FR-ELIC-006**: Linux renderer prefers `zenity`, then `kdialog`,
  then `tkinter`, then `inquire`.
- **FR-ELIC-007**: Headless / SSH detection forces TUI.
- **FR-ELIC-008**: Concurrent requests are routed by `request_id`.
- **FR-ELIC-009**: Timeout defaults to 600s, configurable.
- **FR-ELIC-010**: Secrets are masked when `field.secret = true` or
  `urgency = "secret"`.
- **FR-ELIC-011**: Prompt content is shell-escaped before
  AppleScript/PowerShell interpolation.
- **FR-ELIC-012**: No outbound network calls.
- **FR-ELIC-013**: Tracing events never include entered values.
- **FR-ELIC-014**: Skill manifest is identical across Forge/Codex/Cursor.
- **FR-ELIC-015**: Plugins install via a single shell command per host.

## 13. Absorbed-tool lineage

Nothing to absorb — `elicitate` is a brand-new primitive. It draws
inspiration from:

- **MCP spec's `elicitation` capability** (2025-06-18 spec revision)
- **`inquire` crate** (terminal UX patterns)
- **`rfd` crate** (Rust File Dialogs — considered but rejected: needs GTK/Qt
  runtime, heavier than `osascript`)
- **`native-dialog`** crate (considered; unmaintained since 2023)
- **Apple's `display dialog` AppleScript command** (the inspiration for the
  macOS path)

## 14. Risks & mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| AppleScript injection from agent-authored prompt | high | Shell-escape layer; rejected prompts return `Failed` |
| Popup hangs forever if OS bug | medium | Default 600s timeout; configurable |
| Modal dialog not visible on multi-monitor / virtual desktops | medium | `--parent-pid` focus-stealing hook |
| MCP server gets SIGTERM mid-popup | medium | `setsid` / `CREATE_NEW_PROCESS_GROUP` |
| Plugin install path varies across host versions | medium | Each plugin ships an OS-aware `install.sh` |
| Cursor `mcpServers` schema changes | low | Pin to known-good version; document upgrade path |
| PowerShell execution policy blocks script | medium | Spawn with `-ExecutionPolicy Bypass -NoProfile` |
| macOS sandbox restrictions on `osascript` (some MDM profiles) | medium | Detect and fall back to TUI with clear error |
| User never sees popup because session is locked | low | Document; recommend `--renderer=force-tty` for headless workflows |

## 15. Linkage

- Charter: `phenotype-tooling/charter.md` (will be updated; see plan §6)
- SPEC: `phenotype-tooling/SPEC.md` (will be updated; see plan §6)
- Intent: `phenotype-tooling/intent.md` (will be updated; see plan §6)
- SOTA: `phenotype-tooling/SOTA.md` (will add DX dimension entry)
- Workspace: `phenotype-tooling/Cargo.toml` (add `crates/elicitate` member)
- CLI facade: `phenotype-tooling/crates/phenotype-cli/src/lib.rs` (add
  `Elicitate` variant or use the existing delegated pattern)
- Plans: `repos/plans/2026-07-21-elicitate-EXECUTION-PLAN-v1.md`
- Skill: `phenotype-tooling/crates/elicitate/.elicitate/skills/elicitate/SKILL.md`
- Plugins: `phenotype-tooling/crates/elicitate/plugins/{forgecode,codex,cursor}/`

## 16. What ships in v0.1.0 (this work)

1. Rust crate `elicitate` with library, CLI, and MCP-server binaries.
2. macOS renderer (AppleScript).
3. Windows renderer (PowerShell + Win32 forms).
4. Linux renderer (zenity/kdialog/tkinter/inquire chain).
5. JSON Schema export for `PromptSpec` and `ElicitResponse`.
6. SKILL.md.
7. Plugins for Forge, Codex, Cursor.
8. CLI smoke-test.
9. Unit + integration tests (GUI tests `#[ignore]`d by default).
10. `elicitate serve` MCP server (stdio transport).
11. `phenotype-cli` subcommand delegation (`pt elicitate`).
12. README, CHANGELOG, PRD, SPEC, PLAN, ABSORPTION notes.

What does **not** ship in v0.1.0 (deferred to v0.2):

- HTTP transport for the MCP server (stdio only for v0.1).
- Webview fallback (intentional non-goal).
- Slack/Discord notification fallback.
- Persistent popup history.
- Custom icons beyond the built-in 4 (info/warning/error/secret).
- Linux Wayland native protocol (X11/XWayland/`zenity` covers it).