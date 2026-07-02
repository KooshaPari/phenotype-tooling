# WP-11 — PTX Wrap & Governance Gates

## Goal

Provide a thin `ptx` binary that:

1. Acts as a **single entry point** for the phenotype-tooling workspace.
2. Wraps every absorbed governance-tier subcommand so the rest of the toolchain
   (CI scripts, governance jobs, the cohort scorecard generator, etc.) can
   invoke one binary instead of N different crates.
3. Exposes a stable **manifest** (which gates ran, which version, what status)
   and **report** (human-readable summary) so P6 has a single artefact to grade.
4. Maps every gate's exit code through a documented contract
   (0 = ok, 1 = gate failed, 2 = config error, 3 = infrastructure error).

## Architecture

```
crates/ptx/
├── Cargo.toml          # bin = ptx, name = ptx, deps = clap
└── src/
    ├── lib.rs          # PtxError, ExitCode, SCHEMA_VERSION, all_passed, run_cli
    ├── check.rs        # Gate / Status / GateContext; one check = one absorbed subcommand
    ├── wrap.rs         # PinnedCrate / Lockfile — workspace inventory snapshot
    ├── manifest.rs     # PTX_MANIFEST struct, SCHEMA_VERSION constant
    ├── report.rs       # report::render(&[Gate]) -> String (markdown)
    └── main.rs         # 30-line binary entry → ptx::run_cli()
```

### Module responsibilities

- **`check`** — abstract gate. Each absorbed subcommand implements a
  `GateContext` that knows how to run itself (cmd invocation, parse output,
  produce a `Status`). The unit of work is `Gate { name, status, detail,
  elapsed_ms, stdout_tail, stderr_tail }`. A gate's `Status` is one of:
  `Pass`, `Fail`, `Skip`, `Config`, `Infra`.

- **`wrap`** — workspace inventory. Reads `Cargo.lock`, walks workspace members,
  produces `PinnedCrate { name, version, sha }` rows so the manifest can
  anchor every binary's exact pins. This is what makes a PTX run
  **reproducible** across machines.

- **`manifest`** — JSON output with `SCHEMA_VERSION` so consumers can pin
  to a known shape. Format is `{"schema_version": 1, "crates": [...],
  "gates": [...], "elapsed_ms": N, "pinned_at": "ISO-8601"}`.

- **`report`** — markdown summary suitable for GitHub PR comments. Reads
  the same `Gate[]` slice and emits a section per gate with status icon,
  detail, and a copy-paste line for the audit ledger.

- **`main.rs`** — three lines: `ptx::run_cli()` → `match` on the typed
  result → `ExitCode`. The CLI flag surface is entirely in `lib.rs`.

## Exit-code contract

| Code | Meaning | Reporter action |
|---|---|---|
| 0 | All gates passed or skipped | None |
| 1 | At least one gate reported `Status::Fail` | Re-run that gate in isolation |
| 2 | A gate reported `Status::Config` (bad args, missing file) | Fix the config; do not retry |
| 3 | A gate reported `Status::Infra` (network, lock, IO) | Retry after backoff |
| 64 | PtxError (PTX itself broken) | File an issue |

CI MUST treat codes 1/2/3 as different failure classes — a code 2 should NOT
trigger the bench regression re-run, and a code 3 should retry once before
failing.

## Acceptance criteria

- [ ] `cargo build -p ptx` succeeds with zero `missing_docs` warnings
- [ ] `ptx --help` lists the gate set
- [ ] `ptx` writes `ptx-manifest.json` and `ptx-report.md` next to the cwd
- [ ] `ptx --gate <name>` runs a single gate and prints a one-line verdict
- [ ] All absorbed subcommands invokable through `ptx wrap <subcommand>`
- [ ] Exit codes follow the documented contract
- [ ] `ptx` is reproducible: re-running produces an identical manifest
      given an identical `Cargo.lock`