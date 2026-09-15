# Gateway vendor pins (H10)

Submodule SHAs from [phenotype-gateway](https://github.com/KooshaPari/phenotype-gateway) `third_party/` as of 2026-06-19.

| Plane | Submodule | SHA |
|-------|-----------|-----|
| Agent terminal API | `agentapi-plusplus` | `5ae7736522ebf41480386821e3e4474d951b974d` |
| CLI proxy | `cliproxyapi-plusplus` | `541025785c8ae7de2c6d35888a13f349a5d72c6e` |
| Enterprise gateway | `bifrost` | `9c0d904e3653a22c4d9e90fedadb9d6a6983cbcb` |
| Plugins / SLM | `argis-extensions` | `69b447e2a52237e0d69518cfc6c3792700934ebf` |

## Context

- H9 smoke gates green at these pins (phenotype-gateway #6, #12).
- H10 promotion anchors: `packages/cliproxy`, `packages/agentapi`, `packages/router` (phenotype-gateway #14).
- G16 follow-up: refresh any go-sdk consumer docs when gateway submodule bumps land.

## References

- [GATEWAY_FEATURE_PARITY](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/rationalization/GATEWAY_FEATURE_PARITY.md)
- [PROMOTION.md](https://github.com/KooshaPari/phenotype-gateway/blob/master/docs/PROMOTION.md)
