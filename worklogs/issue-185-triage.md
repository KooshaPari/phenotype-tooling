# Issue triage note — 2026-06-23

GitHub issue **#185** ("Mach-O binary paste reference aborts Forge turn")
was filed against `KooshaPari/phenotype-tooling`, but it describes a bug
in **Forge**, a separate Electron-based CLI / chat composer at
`/Users/kooshapari/.local/bin/forge` (referenced as `contentscript.js:14083`,
`MiniMax-M3` / `OmniRoute` blend, `@file` paste guard, stop-hook chain).

`phenotype-tooling` is a Rust workspace for internal org tools
(`agent-forecast`, `anthropic-usage-poll`, `temporal-grounding`,
`worktree-manager`, `byteport`, …) plus a thin Svelte/TypeScript wrapper
around an MCP `cheap_llm` provider. It does **not** contain:

- any chat composer, file-paste, or `@file` reference logic,
- a `contentscript.js` renderer,
- a stop-hook chain,
- a `ToolResultBlock` model,
- a `forge.tools.file.maxBytes` config,
- the `application/x-mach-binary` MIME guard referenced in the issue.

No code under `crates/`, `src/`, `packages/`, or `docs/` matches the
failing call sites (`grep` for `application/x-mach-binary`,
`Binary files are not supported`, `ToolResultBlock` outside absorbed
docs, `MaxListenersExceeded`, `forge.tools.file.maxBytes` returns no
matches in this repository's own source). The only `ToolResultBlock`
references are in `docs/absorbed-from-heliosApp/` and `crates/heliosapp/`,
both of which are absorbed reference docs for unrelated apps.

The reproduction steps in #185 also reference a different branch
(`chore/v25-71-pillar-cycle-15-p1-2026-06-22`) and a worktree
(`phenotype-apps-L39-wt/dagctl`) that do not exist in this repo.

**Action:** No code change is possible in this repository. The issue
needs to be re-filed against the upstream `forge` source repo (likely
`KooshaPari/forge` or whatever hosts the CLI bundle at
`/Users/kooshapari/.local/bin/forge`). This file exists so future
agents do not re-spend context searching for a non-existent bug here.