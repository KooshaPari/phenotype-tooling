# Intent — phenotype-go-sdk

## Problem statement

Phenotype-org Go platform code (DevHex, PlatformKit, McpKit Go modules) was scattered across standalone repos with duplicated modules, broken `go.work` references, and no fleet-wide governance. Agents could not infer which Go module path is canonical or when Go is justified vs Rust/Python SDK cores.

## Success criteria

- [ ] Single canonical Go workspace with clean `go work sync` for active packages
- [ ] PlatformKit duplicate modules removed; devhex is sole devenv module owner
- [ ] Genesis doc set (charter, review, intent, SOTA, OKF) linked and agent-readable
- [ ] Go language placement documented in SOTA (Tier 3 justified edge)

## Non-goals

See [charter.md](charter.md#out-of-scope). Key exclusions:

- Rust developer tooling (owned by `phenotype-tooling`)
- Static analysis runtime (owned by `KodeVibe`)
- Python SDK packages (owned by `phenotype-python-sdk`)

## Originating prompts

Deterministic provenance in [docs/intent/prompts/](docs/intent/prompts/README.md).

| Date | Tool | Session | Summary |
|------|------|---------|---------|
| 2026-06-16 | cursor | genesis-rollout | [platform role + Go edge genesis docs](docs/intent/prompts/.gitkeep) |

Refresh: `python scripts/extract-intent-prompts.py --out-dir docs/intent/prompts --repo phenotype-go-sdk`

## Synthesized goals

Full synthesis: [docs/intent/synthesis.md](docs/intent/synthesis.md)

**Confirmed (user-stated):**

1. Own the `platform` domain role for Go modules (devhex, devenv, MCP Go workspace)
2. Bootstrap genesis governance from HexaKit `templates/genesis/`
3. Document Go as Tier 3 justified edge per `phenotype-registry` LANGUAGE_PLACEMENT

**Inferred (needs validation):**

1. McpKit Go packages restore when `pheno-mcp-*` modules are available
2. platformkit remains docs/specs-only after ADR-011 convergence

## Agent assumptions log

| Assumption | Action taken | Validated? |
|------------|--------------|------------|
| User wants genesis rollout on `feat/genesis-docs-rollout` | Copied and customized genesis template | pending |
| Go is justified for devenv/devhex ecosystem lock-in | Added SOTA technical.md language placement | pending |

Details: [docs/intent/assumptions.md](docs/intent/assumptions.md)
