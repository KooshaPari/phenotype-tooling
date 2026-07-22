# elicitate — Product Requirements Document

## Authors

- Owner: `phenotype-tooling/elicitate`
- Status: Draft → ready-for-implementation
- Target version: 0.1.0
- Reviewers: `agent-orchestrator`, `phenotype-cli`, `release-cut`

## Why now

Across the Phenotype ecosystem (Forgecode, Codex, Cursor), every agent that wants a missing decision
today must reach for the chat pane. This breaks the agent's flow and forces the operator to switch
contexts. A native, modal, single-decision prompt — fired from the agent's tool loop — solves it.
The required building blocks already exist in `phenotype-tooling` (rmcp scaffolding, dispatch router,
skill manifest conventions). What's missing is the renderer core and the cross-client plugin glue.

## Product definition

`elicitate` is a Rust crate that ships:

- A library (`elicitate::elicit`) callable from any host agent that imports it.
- A CLI (`elicitate`) usable as a subprocess from any language.
- An MCP server (`elicitate-mcp`) consumable by every MCP-aware client.
- Three first-party plugins (Forgecode, Codex, Cursor) and one universal skill manifest.

It opens a **native popup window** on macOS and Windows. On Linux it opens a GTK4 dialog or, if no
display is available, a TUI prompt. On headless systems it goes straight to TUI. All four rendering
paths consume the same JSON spec and emit the same JSON response.

## User stories

1. **As a Forgecode agent**, I need the operator to confirm before I rename 23 identifiers across 8
   files, so I can `elicitate` a boolean and proceed without chat interruption.

2. **As a Codex agent**, I need an Anthropic API key the operator hasn't set yet, so I can
   `elicitate` a `secret: true` text field, capture the masked input, and continue.

3. **As a Cursor agent**, I need the operator to pick a deployment target (Staging / Canary / Prod),
   so I `elicit` a `choice` and dispatch the deploy.

4. **As an operator**, I want every prompt to feel like a system dialog — small, modal, dismissed
   with the same shortcuts I'm used to — so the agent never feels like a webpage.

## Functional requirements

| ID    | Requirement                                                                                            |
| ----- | ------------------------------------------------------------------------------------------------------ |
| F-01  | The library accepts a `PromptSpec` JSON and returns an `ElicitResponse`.                               |
| F-02  | The CLI accepts the same spec via flags or stdin and emits the same response on stdout.                |
| F-03  | The MCP server exposes a single tool `elicitate_mcp` with the spec as input schema.                    |
| F-04  | The macOS renderer uses AppKit (`NSPanel` / `NSWindow` + standard `NSControls`) and is modal to the active app. |
| F-05  | The Windows renderer uses Win32 (`CreateWindowExW` + standard controls) and is modal to the owner window. |
| F-06  | The Linux renderer uses GTK4 (`rfd`) when a display is available, otherwise TUI.                       |
| F-07  | A TUI fallback exists using `inquire`, always accepting the same input shape and emitting the same JSON. |
| F-08  | All renderers honor `timeout_secs`. On timeout, the prompt is dismissed and the response is `timed_out`. |
| F-09  | Secret fields are masked in the GUI and never logged.                                                   |
| F-10  | The schema is published as JSON Schema (`elicitate schema` and `elicitate::schema_json()`).            |
| F-11  | Plugins for Forgecode, Codex, and Cursor install the binary and register the MCP server / skill.       |
| F-12  | A universal skill manifest lives at `.elicitate/skills/elicitate/SKILL.md` and is consumable by all clients. |

## Non-functional requirements

| ID    | Requirement                                                                                            |
| ----- | ------------------------------------------------------------------------------------------------------ |
| N-01  | First-paint latency: ≤ 500 ms on warm start (binary already launched once).                            |
| N-02  | Cold start: ≤ 1.5 s on M-series Mac, ≤ 2.0 s on Windows 11.                                            |
| N-03  | Binary size: ≤ 25 MB stripped (the Windows release; macOS is smaller).                                 |
| N-04  | Zero outbound network dependencies.                                                                    |
| N-05  | All public types implement `Serialize + Deserialize` and roundtrip through `serde_json`.                |
| N-06  | No panics on user input. Invalid spec → `ElicitError::InvalidSpec(String)`.                            |
| N-07  | Cross-platform test suite runs on `cargo test -p elicitate` without a display server.                  |

## Risks

| Risk                                                                                  | Mitigation                                                  |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| AppKit requires main thread; mixing with `tokio` runtime is brittle.                  | Run the GUI on a dedicated blocking thread; tokio runtime stays clean. |
| `windows-sys` is large and slow to compile.                                            | Gate behind a feature flag (`gui-windows`); TUI-only build is fast. |
| Operators on locked-down macOS may not have Accessibility / Automation entitlements. | The macOS renderer is a passive prompt — no entitlements required (modal sheet attached to the active app via `setSheetParent`). |
| Cursor's MCP transport changes between versions.                                      | Plugin's `install.sh` detects Cursor version and writes the right key (`mcp` for v0.40+, `mcpServers` for older). |
| An agent can spin up unbounded popups.                                                | The MCP server enforces `max_concurrent_prompts = 1`. A second call blocks until the first resolves or times out. |

## Out of scope (v0.1)

- Multi-page wizards.
- Drag-and-drop file pickers (we provide `FieldSpec::Path` but no DnD UI yet).
- Localized button labels (UI strings are English-only; i18n is a follow-up).
- Server-rendered prompts (HTTP transport) — stdio only for v0.1.

## Success metrics

- A reviewer can `cargo install --path crates/elicitate` and have a working `elicitate` and
  `elicitate-mcp` in under five minutes.
- Forgecode + Codex + Cursor all list `elicitate_mcp` after running their respective `install.sh`.
- CI passes: `cargo test -p elicitate` and `elicitate-mcp` round-trips a `tools/list` request.
- The macOS renderer ships a notarizable `.app` bundle (handled in a separate `release-cut` plan).
