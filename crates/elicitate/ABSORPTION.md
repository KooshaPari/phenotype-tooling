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

## Conventions adopted

- **Library naming.** Crates inside `phenotype-tooling` use `kebab-case` (`elicitate`, `release-cut`).
- **Subcommands.** Cli subcommands are spelled out (`ask`, `validate`, `schema`, `detect`).
- **Skill manifests.** Universal skills live at `.elicitate/skills/<skill-name>/SKILL.md`. This is
  the first crate to use the `.elicitate` prefix inside its own root; we adopt it for namespace
  clarity (avoid clashing with the host repo's `.github/`, `.vscode/`, etc.).
- **MCP transport.** Stdio only for v0.1; HTTP deferred to v0.2.

## Risks introduced by the absorption

- We add two new native-UI dependencies (`objc2` + `cocoa` on macOS, `windows-sys` on Windows).
  These are well-maintained crates but pull in significant compile time on CI. Mitigation: gate the
  GUI behind feature flags; default build (CI) is GUI-free and uses the TUI renderer.

## Sign-off

- Author: `elicitate` initial author
- Reviewer: `release-cut` owner
- Date: 2026-07-21
