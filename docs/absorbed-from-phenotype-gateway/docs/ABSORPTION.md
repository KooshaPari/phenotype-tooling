# H10 absorption model — submodule canonical, packages boundary

Per [ADR-ECO-014](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/adrs/ADR-ECO-014-phenotype-gateway-charter.md), phenotype-gateway **does not fork** Go planes into duplicate canonical trees.

## Absorption pattern (H10 complete)

| Plane | Canonical source | Gateway boundary | Status |
|-------|------------------|------------------|--------|
| cliproxy++ | `third_party/cliproxyapi-plusplus` | `packages/cliproxy` | anchor + smoke |
| agentapi++ | `third_party/agentapi-plusplus` | `packages/agentapi` | anchor + smoke |
| bifrost | `third_party/bifrost` | `packages/bifrost` | anchor + smoke |
| argis | `third_party/argis-extensions` | `packages/argis` | anchor + smoke |
| router revamp | `spikes/rust/router` | `packages/router` | ComboVariant + HTTP delegate |

**Anchor packages** mark the promotion boundary (PIN/BOUNDARY). Implementation stays in submodules; gateway owns integration, smoke, and router revamp.

## Smoke matrix

```bash
task smoke          # third_party Go planes + packages/* anchors
task router:test    # Rust router spike + packages/router
```

## Non-goals

- Copying cliproxy/agentapi/bifrost/argis source into `packages/` (duplicate canonical)
- Piecemeal Rust rewrite of Go planes
