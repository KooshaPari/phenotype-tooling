# cliproxyapi-plusplus (pinned reference)

**ADR:** ADR-ECO-007 Option B — canonical proxy plane for phenotype-go-sdk integrations.

| Field | Value |
|-------|-------|
| Upstream | https://github.com/KooshaPari/cliproxyapi-plusplus |
| Branch | `main` |
| Pinned SHA | `541025785c8ae7de2c6d35888a13f349a5d72c6e` |
| Pinned at | 2026-06-19 (Phase 4 H9 gate refresh) |
| Commit subject | fix(smoke): guard syscall.Umask for non-Unix builds (#1033) |

## Usage

This directory documents the cliproxyapi-plusplus commit that phenotype-go-sdk targets. It is not a full vendor subtree; bump the SHA here when intentionally advancing the proxy-plane boundary.

## Related

- [VIBEPROXY_ABSORPTION.md](https://github.com/KooshaPari/cliproxyapi-plusplus/blob/541025785c8ae7de2c6d35888a13f349a5d72c6e/VIBEPROXY_ABSORPTION.md) — vibeproxy client absorption notes
- [vibeproxy](https://github.com/KooshaPari/vibeproxy) — deprecated Swift client (redirect only)
- phenotype-gateway pin: `third_party/cliproxyapi-plusplus` @ `54102578` ([#12](https://github.com/KooshaPari/phenotype-gateway/pull/12))
