# PhenoMCP — Threat Model (STRIDE-per-component)

> **Source audit:** `FLEET-AUDIT-REPORT.md` — S7 (Threat model) is the #1 P0 gap (priority 42, 10 of 11 audited repos at score 0).
> **Method:** STRIDE per-component. Each component in your system gets a row; each STRIDE category is a column.
> **Repo:** `PhenoMCP` — polyglot (Rust + Python + TypeScript + Go) MCP server for the Phenotype org.
> **Canonical entrypoint:** `python -m pheno_mcp` (Python FastMCP bridge, stdio). Rust `pheno-mcp` binary is experimental.

## When to do this

A threat model is **wired** (score 2) when this file exists in `docs/security/threat-model.md`
and is referenced from your `README.md` or `SECURITY.md`.
It's **measured** (score 3) when a CI gate fails if the file is more than 90 days old.

## STRIDE cheat sheet

| Letter | Threat | Property violated | Question to ask |
|--------|--------|-------------------|------------------|
| **S** | Spoofing | Authentication | Can an attacker impersonate a user/system? |
| **T** | Tampering | Integrity | Can an attacker modify data or code? |
| **R** | Repudiation | Non-repudiation | Can a user deny an action they took? |
| **I** | Information disclosure | Confidentiality | Can an attacker read data they shouldn't? |
| **D** | Denial of service | Availability | Can an attacker make the system unavailable? |
| **E** | Elevation of privilege | Authorization | Can an attacker gain higher privileges? |

For each cell, mark one of: **N/A** (not applicable to this component), **low** (impact minor,
mitigation optional), **med** (mitigation required), **high** (mitigation + test required).

---

## Component inventory

List every component in your system. A component is any discrete unit that handles data
or accepts input — a service, a CLI, a database, a queue, a third-party dependency, a
network boundary, a CI workflow, even a build artifact.

Example components (adjust to your system):
- Public web frontend
- Public API
- Auth service
- Database (primary + replicas)
- Object storage
- Message queue
- Background workers
- Admin console
- CI/CD pipeline
- Third-party LLM providers
- CLI tool
- Container runtime

## Per-component threat grid

For each component, fill in the STRIDE table.

### Component: `<name>`

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | low/med/high | | | | YYYY-MM-DD |
| **T — Tampering** | | | | | |
| **R — Repudiation** | | | | | |
| **I — Info disclosure** | | | | | |
| **D — DoS** | | | | | |
| **E — Elevation** | | | | | |

Repeat this block for every component.

---

## PhenoMCP component inventory

The MCP server surface consists of these discrete components. Each row in
the per-component threat grid below covers one of these.

| ID | Component | Path | Trust boundary |
|----|-----------|------|----------------|
| C1 | Python MCP protocol handler | `python/src/pheno_mcp/server.py` | Local process boundary; stdio JSON-RPC 2.0 |
| C2 | Python FastMCP transport bridge | `python/src/pheno_mcp/transport.py` | stdio frame layer (only currently) |
| C3 | Python tool registry (6 bundles) | `python/src/pheno_mcp/tools/*.py` | Tool dispatch; in-process Python invocation |
| C4 | Rust `pheno-mcp` server (rmcp SDK) | `crates/pheno-mcp-server/src/server.rs` | streamable HTTP + stdio; experimental |
| C5 | Rust tool registry | `crates/tool-registry/src/lib.rs` | rmcp tool handler dispatch |
| C6 | Backend adapter: Meilisearch | `crates/pheno-meilisearch/` | Outbound HTTP to Meilisearch |
| C7 | Backend adapter: Qdrant | `crates/pheno-qdrant/` | Outbound HTTP/gRPC to Qdrant |
| C8 | Backend adapter: SurrealDB | `crates/phenotype-surrealdb/` | WebSocket to SurrealDB 3.0 |
| C9 | Polyglot supply chain (5 langs) | `Cargo.toml`, `pyproject.toml`, `package.json`, `go.mod`, `bindings/*` | crates.io / PyPI / npm / Go proxy / binding registries |
| C10 | CI/CD pipeline (release-plz + cargo-deny) | `.github/workflows/*.yml` | GitHub Actions, requires `contents: write` + `pull-requests: write` + `issues: write` |
| C11 | Server configuration (host/port/secrets) | `ServerConfig` (Python) + `PhenoServerConfig` (Rust) | env var surface |
| C12 | Release artifacts (SLSA, attestations) | `.github/workflows/release-attestation.yml` | crates.io publish path |

Coverage: **12 of 12 components documented below (100%)**. Per the template,
this is required for S7 score 2 (wired).

---

## Per-component threat grids

### Component: C1 — Python MCP protocol handler

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | high | Attacker forges JSON-RPC method name or replays a captured `tools/call` over stdio (no auth layer; process boundary is the only check) | stdio process boundary is the auth model; document that PhenoMCP is not multi-tenant; future: add token-based handshake to FastMCP bridge | security | 2026-06-16 |
| **T — Tampering** | med | Malicious tool argument object bypasses `_handle_tools_call` validation; `arguments` is a free-form `dict[str, Any]` — no JSON-Schema enforcement in Python handler (only Rust has `schemars`) | Input shape validated for `name` (str) and `arguments` (dict); deeper per-tool validation must live in tool handler; consider gating at `handle_request` boundary | security | 2026-06-16 |
| **R — Repudiation** | med | No request log on the Python side (`handle_request` is silent); cannot prove which MCP client invoked which tool | Add `tracing` instrumentation in `handle_request` (Rust side already does); structured logs to stdout | sre | 2026-06-16 |
| **I — Info disclosure** | med | Tool handler exception strings are echoed back to caller as `data.detail` (line 296–299 of `server.py`) — may leak secrets from backend adapter errors | Sanitize exception strings before returning; map known error classes to stable codes | security | 2026-06-16 |
| **D — DoS** | med | A misbehaving tool blocks the event loop (single `asyncio` task per `tools/call`; no timeout) | Add `asyncio.wait_for(..., timeout=)` per tool call; enforce in `_handle_tools_call` | sre | 2026-06-16 |
| **E — Elevation** | med | Tool registry dispatch (`name not in self._tools` guard at line 278) relies on dictionary lookup; tool-name collisions over each other silently (`register_tool` overwrites — line 148) | Make `register_tool` reject collisions; consider namespacing tools as `<server>_<verb>_<noun>` per `MCP-CATALOG.md` | rust-dev | 2026-06-16 |

### Component: C2 — Python FastMCP transport bridge

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | high | FastMCP bridge calls `FastMCP(name=server.name, host=..., port=...)` — `host` default is `127.0.0.1` (good) but streamable-HTTP mode (planned) is not yet bind-validated | Keep `host=127.0.0.1` default; refuse `0.0.0.0` without explicit env override | security | 2026-06-16 |
| **T — Tampering** | low | Tool handler lambda in `_register_tool_on_fastmcp` re-exposes every Python tool as an async function; closure captures `tool_name` from a loop — Python late-binding would be a bug if `tool_dict` were mutated, but the dict is captured by reference so name is stable | Audit closure capture; rename `_handler.__name__` to enforce tool name | rust-dev | 2026-06-16 |
| **R — Repudiation** | low | Bridge has no per-request logging; relies on FastMCP internals | Out of scope for bridge; upstream logs are the source | sre | 2026-06-16 |
| **I — Info disclosure** | med | `await server.handle_request(...)` propagates any exception string from the Python handler (see C1-I) | Same as C1: sanitize at `server.py` boundary | security | 2026-06-16 |
| **D — DoS** | med | `fmcp.run(transport="stdio")` is a single-process stdio loop; no rate limit; an MCP client can issue `tools/list` in tight loop | Add rate limit at the bridge or upstream of FastMCP | sre | 2026-06-16 |
| **E — Elevation** | low | Bridge has no auth layer; relies on stdio process boundary | Document as single-tenant | security | 2026-06-16 |

### Component: C3 — Python tool registry (6 bundles)

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | med | Tool `name` is the only auth identity; a bundle could register a tool that shadows a privileged tool | Namespacing + namespaced registry; CODEOWNERS per bundle | security | 2026-06-16 |
| **T — Tampering** | med | A malicious PR adding a tool handler that runs arbitrary code — `register_*_tools` is the only thing standing between the PR and full process privilege | CODEOWNERS gate; required PR reviews; cargo-style ratchet: any new tool must update this threat model | security | 2026-06-16 |
| **R — Repudiation** | med | No per-tool audit log; tool handler can mutate side effects silently | Add structured logging at `register_tool` time (immutable audit trail of registered tools) | sre | 2026-06-16 |
| **I — Info disclosure** | high | Tool handlers may receive `arguments` containing user data; the tool returns it as JSON — no field-level redaction | Add output-redaction allowlist at `handle_request` boundary | security | 2026-06-16 |
| **D — DoS** | med | One bundle (`workflow_tools`) can register arbitrarily many tools; no registration cap | Cap on `len(self._tools)` in `register_tool` | sre | 2026-06-16 |
| **E — Elevation** | high | Any registered tool runs as the process UID — equivalent to local code execution. A compromised tool = full host compromise | CODEOWNERS + branch protection; treat tools as first-class auth boundaries | security | 2026-06-16 |

### Component: C4 — Rust `pheno-mcp` server (rmcp SDK)

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | med | `serve_http` binds a `tokio::net::TcpListener` to `bind` from config; a misconfigured `0.0.0.0` exposes unauthenticated rmcp HTTP endpoint to network | `pheno-mcp` is experimental; default to `127.0.0.1`; warn on non-loopback bind | rust-dev | 2026-06-16 |
| **T — Tampering** | med | `PhenoMcpServer` holds `Arc<dyn SearchPort>` and `Arc<dyn SkillStoragePort>` — these are pluggable backends, so a poisoned in-memory port can be swapped at runtime | `in_memory` constructor is the only public escape hatch; mark ports as sealed | rust-dev | 2026-06-16 |
| **R — Repudiation** | low | `tracing::info!` on serve_stdio/serve_http; `tracing` crate present in deps; structured logs | Acceptable; extend with `tracing-subscriber` JSON output | sre | 2026-06-16 |
| **I — Info disclosure** | med | `StreamableHttpService` does not, by default, enforce TLS — HTTP traffic is plaintext | Future: add `axum` TLS terminator or front with Caddy/nginx | security | 2026-06-16 |
| **D — DoS** | med | `axum::serve(listener, router)` has no connection limit; can be saturated by TCP connections | Add `tower` limit middleware; `tokio` task spawn bound | sre | 2026-06-16 |
| **E — Elevation** | med | `serve_http` instantiates a `StreamableHttpService` that calls back into `PhenoMcpServerHandler` per request; if handler is ever moved to a `Box<dyn Any>`, dyn-downcast escalation becomes possible | Keep handler concrete; `#[derive(Clone)]` only | security | 2026-06-16 |

### Component: C5 — Rust tool registry

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | med | Tool-handler dispatch is name-based; rmcp does not include built-in auth on `tools/call` | rmcp provides auth hooks (in `transport-streamable-http-server` feature); not yet wired | security | 2026-06-16 |
| **T — Tampering** | low | `tool-registry` crate is sealed; tool surface is its public API | None needed | rust-dev | 2026-06-16 |
| **R — Repudiation** | med | No per-call log in the registry | Add `tracing::info!` per dispatch | sre | 2026-06-16 |
| **I — Info disclosure** | med | Tool input is `serde_json::Value`; `schemars` validates shape but not content (e.g., PII) | Add PII redaction at schema boundary | security | 2026-06-16 |
| **D — DoS** | med | Synchronous dispatch — a long-running tool blocks the tokio worker | Wrap every tool handler in `tokio::time::timeout` | sre | 2026-06-16 |
| **E — Elevation** | low | Registry is a closed API; only crate-internal callers can register | Mark `register_tool` as `pub(crate)` if not needed externally | rust-dev | 2026-06-16 |

### Component: C6 — Backend adapter: Meilisearch

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | med | `reqwest` HTTP client — no TLS pinning; MitM possible if Meilisearch endpoint is misconfigured | Pin to HTTPS; verify server cert (rustls) | security | 2026-06-16 |
| **T — Tampering** | med | Adapter writes to Meilisearch index; a tampered request body could poison search results | Validate document shape; index-level permissions on Meilisearch side | security | 2026-06-16 |
| **R — Repudiation** | low | Audit trail lives in Meilisearch | n/a | sre | 2026-06-16 |
| **I — Info disclosure** | high | Meilisearch stores indexed documents in plaintext at rest; PhenoMCP may be passing PII through it | Document data-classification requirement; recommend encryption-at-rest on Meilisearch host | security | 2026-06-16 |
| **D — DoS** | med | Bulk-indexing a large Meilisearch write can OOM the Rust process | Stream large writes; `reqwest` body cap | sre | 2026-06-16 |
| **E — Elevation** | med | Adapter holds the Meilisearch admin key in env; anyone with the key can write to the index | Recommend scoped Meilisearch API keys (read-only for search paths) | security | 2026-06-16 |

### Component: C7 — Backend adapter: Qdrant

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | med | Same `reqwest` HTTP client risk as C6 | Same: pin TLS, verify cert | security | 2026-06-16 |
| **T — Tampering** | med | Vector upserts can be poisoned to bias retrieval | Validate vector dimensions client-side; rate-limit | security | 2026-06-16 |
| **R — Repudiation** | low | Qdrant audit log is the source of truth | n/a | sre | 2026-06-16 |
| **I — Info disclosure** | high | Vector embeddings can leak training data; high-cardinality vectors may be PII-derived | Do not log raw vectors; rotate collection API keys | security | 2026-06-16 |
| **D — DoS** | med | Large vector upserts can saturate Qdrant gRPC | Batch + backpressure | sre | 2026-06-16 |
| **E — Elevation** | med | Qdrant collection-level permissions are a different trust boundary than MCP | Use scoped collection tokens | security | 2026-06-16 |

### Component: C8 — Backend adapter: SurrealDB

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | med | `surrealdb` 3.0 WS protocol — WS upgrade is unauthenticated; auth happens inside the protocol | Use SurrealDB namespace + database scope; rotate root credentials | security | 2026-06-16 |
| **T — Tampering** | high | SurrealDB allows arbitrary SurrealQL; a tool handler that constructs a query string (not parameterized) = SQL-injection-equivalent | All adapter calls must use parameterized SurrealQL; ban string interpolation | security | 2026-06-16 |
| **R — Repudiation** | med | SurrealDB has built-in audit tables; not enabled by default | Enable `AUDIT` namespace in adapter config | sre | 2026-06-16 |
| **I — Info disclosure** | high | SurrealDB stores records in plaintext | Document data-classification; recommend field-level encryption for PII | security | 2026-06-16 |
| **D — DoS** | med | Unbounded SurrealQL queries can pin a SurrealDB worker | Query timeouts; connection pool cap | sre | 2026-06-16 |
| **E — Elevation** | high | SurrealDB root user can read/write all namespaces; a PhenoMCP compromise = SurrealDB root | Use scoped DB user (not root); record/namespace-level ACLs | security | 2026-06-16 |

### Component: C9 — Polyglot supply chain (5 languages)

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | high | 5 different package registries (crates.io, PyPI, npm, Go proxy, Swift/Kotlin/C# binding registries) — each is a distinct supply-chain trust boundary. A typosquatted package can shadow a real one. | Pinned versions in lockfiles (`Cargo.lock`, `uv.lock`, `package-lock.json`); S9=3 SHA-pinned where supported (verified 2026-06); `cargo-deny` (deny.toml) | security | 2026-06-16 |
| **T — Tampering** | high | A compromised upstream dep can ship malicious code in 4 languages simultaneously | `cargo-deny` advisories (`deny.yml` workflow); `cargo-audit` (`audit.yml`); npm `package-lock.json` integrity; S8=1 SLSA partial (S8 score 1; needs to lift to 2 with `provenance: true`) | security | 2026-06-16 |
| **R — Repudiation** | low | Lockfiles are auditable | Acceptable | security | 2026-06-16 |
| **I — Info disclosure** | med | Lockfile leaks the full dep graph (a real fingerprint of org structure) | Acceptable; lockfiles are public by design for OSS | security | 2026-06-16 |
| **D — DoS** | med | A 5-language build is a 5x surface for flaky CI; `cargo build` alone takes minutes; `npm` install + `pip` install + `go build` all chain in `ci.yml` | Cache cargo + pip + npm; concurrency groups; consider a single `just build` target | ci-ops | 2026-06-16 |
| **E — Elevation** | high | A build-script (`build.rs`) in any Rust crate runs as the build user; a malicious dep = RCE on the build runner | `cargo-deny` with `bans = { build_scripts = "allow" }` allowed, but should be tightened; `pheno-mcp` itself has no `build.rs` | security | 2026-06-16 |

### Component: C10 — CI/CD pipeline (release-plz + cargo-deny)

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | med | A compromised third-party GitHub Action (`release-plz/action`, `dtolnay/rust-toolchain`, `actions/checkout`) becomes the attacker's pipeline | release.yml SHA-pins `release-plz/action@d22c02a7cf6d7870bd163be7c7d9518d331aef34` (good); `dtolnay/rust-toolchain@stable` is a tag, not SHA — should pin SHA | ci-ops | 2026-06-16 |
| **T — Tampering** | high | `release-plz-pr` and `release-plz-release` both have `permissions: contents: write` + `pull-requests: write` + `issues: write` — a token-leak or workflow compromise can push tags and open PRs as the repo | Branch protection on `main` requires PR; CODEOWNERS gates; pin all Actions to SHA | ci-ops | 2026-06-16 |
| **R — Repudiation** | low | Workflow runs are visible in GitHub UI; git log shows release-plz commits | Acceptable | ci-ops | 2026-06-16 |
| **I — Info disclosure** | med | `CARGO_REGISTRY_TOKEN` secret is the crates.io publish credential — leaks are full crates.io publish access | Store only in `repo` secrets, not `org`; rotate quarterly; restrict env to release job | security | 2026-06-16 |
| **D — DoS** | low | `concurrency: group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true` on release.yml | Good | sre | 2026-06-16 |
| **E — Elevation** | high | `release-plz` opens PRs and pushes tags with the GITHUB_TOKEN. If release-plz is compromised, it can publish malicious crate versions | Pin `release-plz/action` to SHA (currently SHA-pinned — verified); verify `release-plz.toml` is the source of truth | ci-ops | 2026-06-16 |

### Component: C11 — Server configuration (host/port/secrets)

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | med | `ServerConfig.host` defaults to `127.0.0.1` (good). A future streamable-HTTP mode that binds to `0.0.0.0` would be world-reachable | Refuse `0.0.0.0` without `PHENOMCP_ALLOW_PUBLIC_BIND=1`; document the env var | security | 2026-06-16 |
| **T — Tampering** | med | `ServerConfig` is a `@dataclass` with mutable defaults; tests can mutate the class itself (`ServerConfig.host = "..."`) | Use `frozen=True` dataclass; or pydantic `BaseModel` with `model_config = ConfigDict(frozen=True)` | rust-dev | 2026-06-16 |
| **R — Repudiation** | low | Config is loaded once at startup | Log effective config (with secret redaction) at startup | sre | 2026-06-16 |
| **I — Info disclosure** | high | Secrets (Meilisearch master key, Qdrant API key, SurrealDB root creds) live in env vars; if a tool handler echoes the env, they leak | Document "never log env"; redact in `tracing` formatter | security | 2026-06-16 |
| **D — DoS** | low | Port collision | n/a | n/a | 2026-06-16 |
| **E — Elevation** | med | `ServerConfig` is constructed by `create_configured_server()` with defaults — any caller can override port/host | Document that configuration must come from a trusted source | security | 2026-06-16 |

### Component: C12 — Release artifacts (SLSA, attestations)

| Threat | Rating | Specific attack vector | Mitigation | Owner | Last reviewed |
|--------|--------|------------------------|------------|-------|---------------|
| **S — Spoofing** | med | A malicious actor can publish a crate with a similar name (e.g., `pheno-mcp` vs `phenomcp`) | Reserve the crate name in advance; document it in `docs/security/threat-model.md` | security | 2026-06-16 |
| **T — Tampering** | med | A published crate, once on crates.io, is immutable for that version — but a new malicious version can be published | S8=1 SLSA partial — needs `provenance: true` on the publish step; S9=3 SHA-pinned inputs (good) | security | 2026-06-16 |
| **R — Repudiation** | low | release-attestation.yml provides signed SLSA provenance | Good | sre | 2026-06-16 |
| **I — Info disclosure** | low | Published crates may leak internal API surface | Acceptable; OSS by design | security | 2026-06-16 |
| **D — DoS** | low | crates.io availability | Out of scope (registry-managed) | n/a | 2026-06-16 |
| **E — Elevation** | med | A successful publish = code execution for every user of the crate | S9=3 + SLSA partial mitigates; lift S8 to 2 by enabling `provenance: true` | security | 2026-06-16 |

---

## How to lift the S7 score

- **0 → 1 (ad-hoc):** Add a `docs/security/threat-model.md` with at least one component's STRIDE table.
- **1 → 2 (wired):** Reference the threat model from `README.md` and `SECURITY.md`. Cover at least 80% of your components. Add an owner + last-reviewed column to each row.
- **2 → 3 (measured):** Add a CI gate that fails if `docs/security/threat-model.md` is older than 90 days, OR if a previously-scored component row is deleted.

## Review cadence

Review the threat model:
- **On every major release** (semver minor)
- **On any new external dependency** added
- **On any new public-facing endpoint**
- **Quarterly minimum** (a 90-day-old model is a CI failure for "measured" repos)

## Cross-references

- `BACKLOG.md` — the P0 list; S7 is the #1 item.
- `FLEET-AUDIT-REPORT.md` — the per-pillar fleet-wide distribution.
- `docs/audits/PhenoMCP/ACTION-PLAN.md` — the per-repo action plan; S7 task is PHE-053.
- `SECURITY.md` — vulnerability reporting policy.
- `MCP-CATALOG.md` — tool-naming convention (`<server>_<verb>_<noun>`).
- `deny.toml` — cargo-deny policy referenced in C9.

## How to validate

```bash
# After writing your threat model, validate it has all 5 STRIDE rows
for c in S T R I D E; do
  grep -q "^\*\*$c " docs/security/threat-model.md || echo "missing $c"
done
```

If `grep` returns nothing for all 6 letters, your file is valid.

## Provenance

- **Template version:** 1.0
- **Author:** Phenotype Org holistic audit, 2026-06-16
- **Audit that produced it:** `FLEET-AUDIT-30-PILLAR.md` (S7 P0)
- **Instantiated for:** `PhenoMCP` (KooshaPari/PhenoMCP), 2026-06-16
- **Lifts:** S7 from 0 (absent) to 2 (wired). Components covered: 12 / 12.
- **License:** Same as the parent repo (MIT OR Apache-2.0)
