# syntax=docker/dockerfile:1.7
# Multi-stage Dockerfile for the phenotype-tooling workspace.
#
# Build modes:
#   * `ci`       – default CI / dev image, includes all tooling
#   * `test`     – CI test image, runs the full workspace test suite
#   * `bench`    – benchmark image, runs the criterion harness
#   * `runtime`  – distroless image with just the binaries
#   * `<stream>` – WP-29 production runtime image (one per release stream)
#
# WP-29 stream-specific images:
#   docker build --target stream-core   -t phenotype-tooling:stream-core .
#   docker build --target stream-cli    -t phenotype-tooling:stream-cli  .
#   docker build --target stream-ops    -t phenotype-tooling:stream-ops  .
#
# The `ci` target is the one used in `.github/workflows/ci.yml`.

ARG RUST_VERSION=1.83
ARG DEBIAN_RELEASE=bookworm

# ──── Shared base ─────────────────────────────────────────────────────────────
FROM rust:${RUST_VERSION}-${DEBIAN_RELEASE} AS base
LABEL org.opencontainers.image.source=https://github.com/KooshaPari/phenotype-tooling \
      org.opencontainers.image.licenses=MIT

# Non-interactive apt; install only what cargo actually needs at build time.
ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_TERM_COLOR=always \
    CARGO_INCREMENTAL=0 \
    CARGO_NET_RETRY=10

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        pkg-config \
        libssl-dev \
        protobuf-compiler \
 && rm -rf /var/lib/apt/lists/*

# Pre-install sccache for build cache sharing and the cargo subcommands used
# by both CI and local dev.
RUN cargo install --locked --root /usr/local/cargo \
        sccache \
        cargo-deny \
        cargo-audit \
        cargo-machete \
        cargo-nextest

ENV SCCACHE_DIR=/sccache \
    RUSTC_WRAPPER=/usr/local/cargo/bin/sccache

# ──── CI target ───────────────────────────────────────────────────────────────
FROM base AS ci
WORKDIR /workspace

# Copy manifests first so this layer caches separately from source changes.
COPY Cargo.toml Cargo.lock ./
COPY crates/*/Cargo.toml crates/
COPY bin/*/Cargo.toml bin/
# Stub source dirs so cargo metadata works without the real sources yet.
RUN mkdir -p crates/*/src bin/*/src \
 && for d in crates/* bin/*; do echo "// stub" > "$d/src/lib.rs"; done

RUN cargo fetch --locked || cargo fetch

# Now bring in the real sources.
COPY crates crates
COPY bin bin

# Default `cargo build --workspace` plus the smoke CI step.
CMD ["bash", "-lc", "cargo build --workspace --locked && cargo test --workspace --no-run"]

# ──── Test target ─────────────────────────────────────────────────────────────
FROM ci AS test
WORKDIR /workspace
CMD ["bash", "-lc", "cargo nextest run --workspace --locked || cargo test --workspace --locked"]

# ──── Bench target ────────────────────────────────────────────────────────────
FROM ci AS bench
WORKDIR /workspace
CMD ["bash", "-lc", "cargo bench --workspace --locked --no-fail-fast -- --output-format bencher"]

# ──── Runtime: distroless image with just the workspace binaries ──────────────
FROM gcr.io/distroless/cc-debian12 AS runtime
ARG BINARIES="pt hook-entry"
WORKDIR /app
COPY --from=ci /workspace/target/release/pt /app/pt 2>/dev/null || true
COPY --from=ci /workspace/target/release/hook-entry /app/hook-entry 2>/dev/null || true
# Distroless has no shell, so each binary must be run directly via ENTRYPOINT.
ENTRYPOINT ["/app/pt"]

# ──── WP-29: per-stream production images ─────────────────────────────────────
# Each `stream-<name>` target builds the binaries for one release stream and
# packages them into a distroless image. The entrypoint is the stream's
# primary binary (pt for cli, observability-server for ops, dag-scheduler for core).

FROM ci AS stream-cli
WORKDIR /workspace
RUN cargo build --release --locked -p phenotype-cli
FROM gcr.io/distroless/cc-debian12 AS stream-cli-runtime
COPY --from=stream-cli /workspace/target/release/pt /app/pt
WORKDIR /app
EXPOSE 9090
ENTRYPOINT ["/app/pt", "serve"]
CMD ["--channel", "stable"]

FROM ci AS stream-ops
WORKDIR /workspace
RUN cargo build --release --locked -p phenotype-tooling-observability -p sbom-gen
FROM gcr.io/distroless/cc-debian12 AS stream-ops-runtime
COPY --from=stream-ops /workspace/target/release/phenotype-observability-server /app/observability-server 2>/dev/null || \
    COPY --from=stream-ops /workspace/target/release/phenotype-tooling-observability /app/observability 2>/dev/null || true
COPY --from=stream-ops /workspace/target/release/sbom-gen /app/sbom-gen 2>/dev/null || true
WORKDIR /app
EXPOSE 9090 9101
ENTRYPOINT ["/app/observability"]

FROM ci AS stream-core
WORKDIR /workspace
RUN cargo build --release --locked --workspace --exclude phenotype-cli --exclude phenotype-tooling-observability --exclude sbom-gen
FROM gcr.io/distroless/cc-debian12 AS stream-core-runtime
COPY --from=stream-core /workspace/target/release/dag-scheduler /app/dag-scheduler 2>/dev/null || true
COPY --from=stream-core /workspace/target/release/quality-gate /app/quality-gate 2>/dev/null || true
COPY --from=stream-core /workspace/target/release/release-cut /app/release-cut 2>/dev/null || true
WORKDIR /app
EXPOSE 8080 9090
ENTRYPOINT ["/app/dag-scheduler"]