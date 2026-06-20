# MCP subset — gateway absorption map

> **Interim:** OmniRoute MCP server (37 tools) + bifrost MCP + argis plugins  
> **Target:** bifrost enterprise gateway + `packages/argis` plugin plane

## Absorption split

| Capability | Interim owner | phenotype-gateway target |
|------------|---------------|--------------------------|
| MCP HTTP/SSE transport | bifrost | `packages/bifrost` |
| Tool routing / fallback | argis `plugins/toolrouter`, `smartfallback` | `packages/argis` |
| OAuth MCP auth | bifrost + argis `oauthproxy` | Authvault cross-link |
| OmniRoute MCP tools (37) | OmniRoute | **Revamp subset** in `spikes/rust/router` — do not copy TS monolith |

## Minimum revamp subset (router spike)

- Route list / health
- Provider model enumeration (read-through cliproxy++)
- Combo strategy selection (ties to [COMBO_ROUTING.md](./COMBO_ROUTING.md))

## Out of scope for H13

- Full OmniRoute tool parity
- macOS menu-bar MCP (vibeproxy absorbed → cliproxy++)
