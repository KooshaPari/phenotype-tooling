# bifrost (pinned reference)

**ADR:** ADR-ECO-014 — enterprise gateway / inference engine boundary for phenotype-go-sdk integrations.

| Field | Value |
|-------|-------|
| Upstream | https://github.com/KooshaPari/bifrost |
| Branch | `main` |
| Pinned SHA | `9c0d904e3653a22c4d9e90fedadb9d6a6983cbcb` |
| Pinned at | 2026-06-19 (Phase 4 H9 gate refresh) |
| Commit subject | fix(smoke): local monorepo replaces for transports H9 gate (#10) |

## Usage

This directory documents the bifrost commit that phenotype-go-sdk targets. It is not a full vendor subtree; bump the SHA here when intentionally advancing the gateway-plane boundary. Canonical smoke target is `transports/` at this pin.

## Related

- phenotype-gateway pin: `third_party/bifrost` @ `9c0d904` ([#12](https://github.com/KooshaPari/phenotype-gateway/pull/12))
- [VENDOR_PIN.md](https://github.com/KooshaPari/bifrost/blob/9c0d904e3653a22c4d9e90fedadb9d6a6983cbcb/docs/VENDOR_PIN.md)
