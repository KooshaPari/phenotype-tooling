# Upstream fork pins

Governance SSOT: [ADR-ECO-007](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/adrs/ADR-ECO-007-gateway-merge-superset.md) (phenotype-registry).

| Component | Upstream | Koosha fork | Pin policy |
|-----------|----------|-------------|------------|
| **OmniRoute** | diegosouzapw/OmniRoute | OmniRoute | **Canonical `route` peer** — never archive; not an absorption target for phenotype-gateway |
| agentapi | coder/agentapi | agentapi-plusplus | Track releases; merge `sync/upstream-*` |
| cliproxy | router-for-me/CLIProxyAPI | cliproxyapi-plusplus | Plus fork; community providers; Option B peer + `third_party/` pin |
| bifrost | maximhq/bifrost | bifrost | Vendor tag + local-delta branch only |
| vibeproxy | automaze.io (deprecated) | vibeproxy | Deprecated client; README redirect → cliproxy++ only |
| argis | — | argis-extensions | Plugin / SLM plane |

**phenotype-gateway** owns orchestration/spec and submodule pins in `third_party/`; it does **not** subsume OmniRoute, agentapi++, or cliproxy++.

## Submodule pins (`third_party/`)

Pinned at Wave H13 router promotion (2026-06-18). Update via `git submodule update --remote` only after interim canonical `main` gates pass.

| Submodule | Commit SHA | Notes |
|-----------|------------|-------|
| `third_party/agentapi-plusplus` | `78987040ad2112a9142b9407cfd468c984ae253a` | Post H2 branch superset (#531) |
| `third_party/cliproxyapi-plusplus` | `03d976df977b895ad66434baa1bce302c9040765` | go.mod merge fix (#1027) |
| `third_party/bifrost` | `fdca125796d281c17d219acd059f2ea4433cc4cc` | G17 vendor pin `phenotype/vendor-2026-06` (bifrost#7) |
| `third_party/argis-extensions` | `2fe3f952d9a898bbad570a6856487333fb0deaae` | Plugin plane classification (H5) |

## Checkout

```bash
git submodule update --init --recursive
```
