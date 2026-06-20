# Promotion — submodule → `packages/`

Per [ADR-ECO-014](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/adrs/ADR-ECO-014-phenotype-gateway-charter.md) and [GATEWAY_FEATURE_PARITY](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/rationalization/GATEWAY_FEATURE_PARITY.md).

## Checklist (per plane)

- [x] ≥80% feature rows mapped for component
- [x] `go build ./...` smoke green on submodule pin
- [x] Spike README documents pass/fail
- [x] disposition-index `fsm: done` with PR ref
- [x] Absorption boundary in `packages/<plane>/` — anchor model per [ABSORPTION.md](./ABSORPTION.md) (submodule canonical, no duplicate fork)

## Order (H10 complete)

1. cliproxy++ — **anchor** (`packages/cliproxy`) — #14, #15
2. agentapi++ — **anchor** (`packages/agentapi`) — #14
3. bifrost — **anchor** (`packages/bifrost`) — #15
4. argis — **anchor** (`packages/argis`) — #15
5. router — **delegate** (`packages/router` + `spikes/rust/router`) — #14, H10 closeout

## Absorption model

Gateway owns **integration boundaries** (PIN/BOUNDARY/smoke/router delegate). Fork submodules remain source of truth — see [ABSORPTION.md](./ABSORPTION.md).
