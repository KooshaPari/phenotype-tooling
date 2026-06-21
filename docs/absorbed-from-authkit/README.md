<!-- AI-DD-META:START -->
<!-- This repository is planned, maintained, and managed by AI Agents only. -->
<!-- Slop issues are expected and intentionally present as part of an HITL-less -->
<!-- /minimized AI-DD metaproject of learning, refining, and building brute-force -->
<!-- training for both agents and the human operator. -->
![Downloads](https://img.shields.io/github/downloads/KooshaPari/AuthKit/total?style=flat-square&label=downloads&color=blue)
![GitHub release](https://img.shields.io/github/v/release/KooshaPari/AuthKit?style=flat-square&label=release)
![License](https://img.shields.io/github/license/KooshaPari/AuthKit?style=flat-square)
![AI-Slop](https://img.shields.io/badge/AI--DD-Slop%20Expected-orange?style=flat-square)
![AI-Only-Maintained](https://img.shields.io/badge/Planned%20%26%20Maintained%20by-AI%20Agents%20Only-red?style=flat-square)
![HITL-less](https://img.shields.io/badge/HITL--less%20AI--DD-metaproject-yellow?style=flat-square)

> ⚠️ **AI-Agent-Only Repository**
>
> This repo is **planned, maintained, and managed exclusively by AI Agents**.
> Slop issues, rough edges, and AI artifacts are **expected and intentionally
> present** as part of an **HITL-less / minimized AI-DD** metaproject focused
> on learning, refining, and brute-force training both the agents and the
> human operator. Bug reports and contributions are still welcome, but please
> expect AI-generated code, comments, and documentation throughout.
<!-- AI-DD-META:END -->

# AuthKit

[![Build](https://img.shields.io/github/actions/workflow/status/KooshaPari/AuthKit/ci.yml?branch=main&label=build)](https://github.com/KooshaPari/AuthKit/actions)
[![Release](https://img.shields.io/github/v/release/KooshaPari/AuthKit?include_prereleases&sort=semver)](https://github.com/KooshaPari/AuthKit/releases)
[![License](https://img.shields.io/github/license/KooshaPari/AuthKit)](LICENSE)
[![Phenotype](https://img.shields.io/badge/Phenotype-org-blueviolet)](https://github.com/KooshaPari)

**The canonical authentication and authorization repository for the Phenotype ecosystem.**

AuthKit is the result of absorbing **Authvault** (archived) — unifying all Phenotype auth code (Rust, Go, Python, TypeScript) into a single canonical repo. It provides a comprehensive authentication and authorization framework with multi-provider support (JWT, OAuth2, RBAC, ABAC), cryptographic primitives, policy enforcement, and identity management.

> The Authvault repository has been archived. All development now happens here.

## Architecture

AuthKit follows hexagonal architecture:

- **Domain**: Pure business logic (identity, auth, policy, session, vault)
- **Application**: Use cases and auth services (registration, login, token management)
- **Adapters**: JWT, OAuth2, storage (in-memory, PostgreSQL, Redis), hashers (Argon2, bcrypt), KMS, audit, revocation
- **Infrastructure**: Cross-cutting concerns (error handling, logging)
- **Middleware**: Tower/axum middleware for `Authorization: Bearer` validation, PKCE state/session binding

## Crate Layout

| Crate | Path | Purpose |
|-------|------|---------|
| `authkit-core` | `crates/authkit-core/` | Core auth framework — JWT, OAuth2, RBAC, ABAC, session management, vault, middleware |
| `phenotype-auth-contracts` | `crates/phenotype-auth-contracts/` | Auth and policy contract traits |
| `phenotype-cipher` | `crates/phenotype-cipher/` | Cryptography (AES-GCM, ChaCha20, Ed25519, Argon2) |
| `phenotype-crypto` | `crates/phenotype-crypto/` | Cryptographic utilities (hashing, KDF, signing, random) |
| `phenotype-casbin-wrapper` | `crates/phenotype-casbin-wrapper/` | Casbin adapter for policy enforcement |
| `telemetry-wrapper` | `crates/telemetry-wrapper/` | Telemetry and observability integration |

### Multi-Language SDKs

| Language | Path | Status |
|----------|------|--------|
| Go | `go/` | Middleware and auth utilities |
| Python | `python/` | Auth and security bindings |
| TypeScript | `typescript/` | SDK and interface definitions |

## Build

```bash
# Build all crates
cargo build --workspace

# Run all tests
cargo test --workspace

# Run benchmarks
cargo bench --workspace
```

## Quick Start

```rust
use authkit_core::{Authenticator, UserId, Role};

let auth = Authenticator::new("secret_key");
let token = auth.generate_token(&UserId::new(), &[Role::new("admin")]);
```

## Prerequisites

- Rust 1.75+ (see `rust-toolchain.toml`)
- Go 1.24+ (for Go middleware)
- Python 3.11+ (for Python bindings)
- Node.js 18+ (for TypeScript SDK)

## Documentation

- [Functional Requirements](./FRs/)
- [Architecture Decisions](./docs/adr/)
- [Development Plan](./docs/PLAN.md)
- [Specification](./docs/SPEC.md)

## License

MIT — see [LICENSE](./LICENSE).
