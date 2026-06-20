# phenotype-gateway — unified specification

> Single source of truth for the gateway domain. See [GATEWAY_FEATURE_PARITY](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/rationalization/GATEWAY_FEATURE_PARITY.md).

## Planes

1. **Agent terminal API** — HTTP control of CLI agents (Claude Code, Goose, Codex, …)
2. **CLI subscription proxy** — OpenAI-compatible multi-provider proxy
3. **Enterprise gateway** — bifrost-class load balancing, guardrails, MCP
4. **Plugin extensions** — argis routing, SLM, embeddings
5. **Router revamp** — replace OmniRoute interim MVP

## Language strategy

Start from Go-native forks; spike per component in Go / Rust / Zig / Mojo before full absorption.

## Non-goals

- Piecemeal Rust rewrite of OmniRoute without Go stack preservation
- Merging all 100+ bifrost upstream feature branches
