# Intent — phenotype-tooling

## Problem statement

Phenotype-org duplicated shell scripts, Python linters, and standalone tool repos across the fleet. CI quality gates, doc checks, and release tooling lacked a single Rust-first workspace with linked governance for agents.

## Success criteria

- [ ] Consumer repos adopt `quality-gate`, `docs-health`, and federation workflows
- [ ] Absorbed tools (byteport, heliosapp, nanovms, policystack) build from their subdirs without forced unification
- [ ] Genesis doc set linked and agent-readable
- [ ] No new Bash scripts per scripting policy (Rust default)

## Non-goals

See [charter.md](charter.md#out-of-scope). Key exclusions:

- Go platform SDK modules (owned by `phenotype-go-sdk`)
- Static analysis engine runtime (owned by `KodeVibe`)
- Genesis template scaffolding (owned by `HexaKit`)

## Originating prompts

Deterministic provenance in [docs/intent/prompts/](docs/intent/prompts/README.md).

| Date | Tool | Session | Summary |
|------|------|---------|---------|
| 2026-06-16 | cursor | genesis-rollout | [platform/tooling role genesis docs](docs/intent/prompts/.gitkeep) |

Refresh: `python scripts/extract-intent-prompts.py --out-dir docs/intent/prompts --repo phenotype-tooling`

## Synthesized goals

Full synthesis: [docs/intent/synthesis.md](docs/intent/synthesis.md)

**Confirmed (user-stated):**

1. Own `platform/tooling` domain role — Rust CLIs, CI federation, absorbed standalone tools
2. Bootstrap genesis governance from HexaKit `templates/genesis/`

**Inferred (needs validation):**

1. All FocalPoint lift crates reach production parity with source scripts
2. Absorbed subdirs remain independently buildable (no forced single toolchain)

## Agent assumptions log

| Assumption | Action taken | Validated? |
|------------|--------------|------------|
| Genesis rollout on feat/genesis-docs-rollout | Copied and customized genesis template | pending |
| Rust workspace is primary; absorbed stacks keep own build | charter in-scope table | pending |

Details: [docs/intent/assumptions.md](docs/intent/assumptions.md)
