# phenotype-tooling

Consolidated Rust workspace for Phenotype-org developer tooling. Replaces
dozens of duplicated shell and Python scripts scattered across repos with
a small set of clap-based CLIs aligned to the
[scripting language hierarchy](https://github.com/KooshaPari/phenotype-infrakit/blob/main/docs/governance/scripting_policy.md)
(Rust default; no new Bash).

## Crates

| Crate | Purpose | Replaces |
|-------|---------|----------|
| [`docs-health`](crates/docs-health/) | Markdown vale/markdownlint + broken-link scanner | `phenodocs/.airlock/lint.sh`, `phenodocs/scripts/check_docs_links.py` |
| [`fr-trace`](crates/fr-trace/) | FR-NNN -> test traceability scanner | `repos/scripts/traceability-check.py` (+3 duplicates) |
| [`quality-gate`](crates/quality-gate/) | Aggregates `cargo fmt`/`clippy`/`test` pass-fail | 30+ duplicated `scripts/quality-gate.sh` files |
| [`legacy-scan`](crates/legacy-scan/) | Detects shell/Python anti-patterns per scripting policy | `docs/governance/scripting_policy.md` rubric |

## Migration plan

1. **Scaffold (this repo):** clap skeletons emitting stub JSON reports.
2. **Port logic:** port each source script into its crate, preserving exit
   codes and expected output; retain the shell script as a thin wrapper calling
   the Rust binary during the transition.
3. **Roll out:** replace `scripts/quality-gate.sh` in each consumer repo with
   a one-line shim that invokes the released `quality-gate` binary; then
   delete the shim once CI is green.
4. **Decommission:** remove the Python `traceability-check.py` and
   `check_docs_links.py` variants.

Target consumer repos (partial list):
`AgilePlus`, `HexaKit`, `PhenoKits`, `heliosApp`, `Civis`, `PolicyStack`,
`thegent`, `portage`, `phenodocs`, `Pyron`, `phenoDesign`.

## Build

```bash
cargo check --workspace
cargo test --workspace
cargo clippy --workspace -- -D warnings
cargo fmt --check
```

## License

MIT. See [LICENSE](LICENSE).
