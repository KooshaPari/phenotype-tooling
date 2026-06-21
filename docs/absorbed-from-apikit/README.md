# apikit — HTTP toolkit (REST, GraphQL, WebSocket adapters)

> Migrated from the [Apisync](https://github.com/KooshaPari/Apisync) project.
>
> This crate provides a unified HTTP toolkit with adapters for REST, GraphQL,
> and WebSocket protocols, along with application routing, domain middleware,
> and infrastructure logging.

## Provenance

`apikit` is the direct continuation of [Apisync](https://github.com/KooshaPari/Apisync).
The Apisync GitHub repository has been archived and its content — governance
documents, code-governance files, tooling configuration, CI workflows, ADRs,
research notes, and operational docs — has been absorbed into this repository
under canonical paths:

| Apisync source path                | apikit target path                                        |
| ---------------------------------- | --------------------------------------------------------- |
| `README.md`                        | `docs/governance/README.apisync.md`                       |
| `AGENTS.md`, `CLAUDE.md`, `ADR.md` | `docs/governance/{AGENTS,CLAUDE,ADR}.md`                  |
| `STATUS.md`, `PLAN.md`, `PRD.md`   | `docs/governance/{STATUS,PLAN,PRD}.apisync.md`            |
| `SPEC.md`, `FUNCTIONAL_REQUIREMENTS.md`, `TEST_COVERAGE_MATRIX.md` | `docs/governance/{SPEC,FUNCTIONAL_REQUIREMENTS,TEST_COVERAGE_MATRIX}.apisync.md` |
| `CHANGELOG.md`                     | `docs/governance/CHANGELOG.apisync.md`                    |
| `docs/adr/*`                       | `docs/governance/adr/001..005.md`                         |
| `docs/.vitepress/config.mts`       | `docs/governance/.vitepress/config.mts`                   |
| `docs/index.md`                    | `docs/index.apisync.md`                                   |
| `docs/slsa.md`                     | `docs/slsa.md`                                            |
| `docs/journeys/*`                  | `docs/sessions/journeys/`                                 |
| `docs/stories/*`                   | `docs/sessions/stories/`                                  |
| `docs/traceability/*`              | `docs/sessions/traceability/`                             |
| `docs/research/SOTA.md`            | `docs/research/SOTA.md`                                   |
| `.github/workflows/*`              | `.github/workflows/*` (preserved as-is)                   |
| `CODE_OF_CONDUCT.md`, `CODEOWNERS`, `CONTRIBUTING.md`, `SECURITY.md`, `codecov.yml`, `FUNDING.yml`, `CITATION.cff`, `LICENSE` | repo root (preserved as-is) |
| `mise.toml`, `nextest.toml`, `rust-toolchain.toml`, `rustfmt.toml`, `_typos.toml`, `.editorconfig`, `.gitignore`, `.gitattributes`, `.env.example`, `.health-dashboard.yml`, `.pre-commit-config.yaml` | repo root (replaces apikit's prior versions with Apisync's more recent ones) |

The Apisync GitHub repository was archived before this migration and remains
archived; its full source archive is preserved at `/tmp/apisync-final` for
audit purposes. See `CHANGELOG.md` for the dated migration entry.

## Features

- **REST Client**: Typed HTTP client with `get`, `post`, `put`, `patch`, `delete` methods
- **GraphQL Client**: Async query execution with error-aware responses
- **WebSocket Connection**: Full-duplex message send/receive
- **Application Router**: Request routing and handler dispatch
- **Domain Middleware**: Composable middleware pipeline
- **Structured Logging**: Tracing integration with request metadata

## Architecture

```
┌────────────────────────────────────────────────────┐
│                     apikit                          │
│                                                     │
│  ┌─────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │  REST   │  │   GraphQL    │  │   WebSocket   │ │
│  │ Adapter │  │   Adapter    │  │   Adapter     │ │
│  └─────────┘  └──────────────┘  └───────────────┘ │
│                                                     │
│  ┌────────────────────────────────────────────┐    │
│  │            Application Layer               │    │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────┐  │    │
│  │  │ Router   │  │ Handler  │  │Middleware│  │    │
│  │  └──────────┘  └──────────┘  └─────────┘  │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  ┌──────────────┐  ┌──────────────────────────┐    │
│  │   Domain     │  │     Infrastructure       │    │
│  │  (Types)     │  │  (Logging, Config, etc.) │    │
│  └──────────────┘  └──────────────────────────┘    │
└────────────────────────────────────────────────────┘
```

## Quick Start

Add to your `Cargo.toml`:

```toml
[dependencies]
apikit = { git = "https://github.com/KooshaPari/apikit" }
```

```rust
use apikit::adapters::rest::RestClient;

#[tokio::main]
async fn main() {
    let client = RestClient::new("https://api.example.com");
    let data: serde_json::Value = client.get("/endpoint").await.unwrap();
    println!("{data}");
}
```

## Documentation

- [Specification](docs/SPEC.md) — apikit's current technical spec
- [Functional Requirements](docs/FUNCTIONAL_REQUIREMENTS.md) — apikit's current FRs
- [Test Coverage Matrix](docs/TEST_COVERAGE_MATRIX.md) — apikit's coverage tracking
- [Governance](docs/governance/) — agent guides, ADRs, absorbed Apisync governance docs
- [Sessions](docs/sessions/) — absorbed Apisync journeys, stories, traceability
- [Research](docs/research/) — absorbed Apisync research notes
- [Apisync Provenance](docs/governance/README.apisync.md) — original Apisync README

## License

MIT OR Apache-2.0
