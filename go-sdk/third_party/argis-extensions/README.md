# argis-extensions (pinned reference)

**ADR:** ADR-ECO-014 — plugin / SLM plane boundary for phenotype-go-sdk integrations.

| Field | Value |
|-------|-------|
| Upstream | https://github.com/KooshaPari/argis-extensions |
| Branch | `main` |
| Pinned SHA | `0419dcf423373dabd1806e2cd56e1b4a45a1ba78` |
| Pinned at | 2026-06-19 (Phase 4 H9 gate refresh) |
| Commit subject | fix(smoke): commit graphql gen artifacts and align resolvers for H9 gate (#82) |

## Usage

This directory documents the argis-extensions commit that phenotype-go-sdk targets. It is not a full vendor subtree; bump the SHA here when intentionally advancing the plugin-plane boundary.

## Related

- phenotype-gateway pin: `third_party/argis-extensions` @ `0419dcf` (H9 smoke gate)
- Peer plane: [bifrost](https://github.com/KooshaPari/bifrost) (vendored core)
