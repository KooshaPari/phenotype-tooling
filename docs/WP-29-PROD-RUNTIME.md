# WP-29: Production Runtime

Deploys the 3 release streams (core, cli, ops) as production-grade
container images with health-gated rollouts. Closes the "build → ship →
run" loop that Phase 5 left open.

## Architecture

```
              +-----------------+
              | channel-manifest |
              | (cosign-signed)  |
              +-----------------+
                       |
        per stream ref + per stream tag
                       |
   +-------------------+--------------------+
   |                   |                    |
+--------+      +--------+           +--------+
|  cli   |      |  core  |           |  ops   |
| deploy |      | deploy |           | deploy |
+--------+      +--------+           +--------+
   |                |                    |
canary 5%         canary 1%           canary 10%
   |                |                    |
health-gate        health-gate          health-gate
(prometheus)        (prometheus)          (prometheus)
```

Each stream deploys independently with its own canary population, health
gate, and promotion policy. The roll-out observes the WP-09
observability surface: any breach of `cli:dashboard:success_rate` or
`cli:dashboard:startup_p95` SLOs for 5 consecutive minutes aborts the
roll-out and reverts to the previous version.

## Deliverables

### 1. Multi-stage Dockerfile (per-stream targets)

The Dockerfile defines three build targets, one per release stream:

```dockerfile
# syntax=docker/dockerfile:1.7

# Stream: cli (the pt binary + delegated subcommands)
FROM rust:1.82-bookworm AS builder-cli
WORKDIR /build
COPY . .
RUN cargo build --release -p phenotype-cli -p hook-entry
RUN cp target/release/pt /out/pt
RUN cp target/release/hook-entry /out/hook-entry

# Stream: core (the platform libraries + DAG scheduler)
FROM rust:1.82-bookworm AS builder-core
WORKDIR /build
COPY . .
RUN cargo build --release --workspace --exclude phenotype-cli --exclude hook-entry

# Stream: ops (observability + sbom-gen + release-cut)
FROM rust:1.82-bookworm AS builder-ops
WORKDIR /build
COPY . .
RUN cargo build --release -p phenotype-tooling-observability \
                  -p sbom-gen -p release-cut -p ptx

# Runtime: distroless, non-root, read-only root filesystem
FROM gcr.io/distroless/cc-debian12:nonroot AS runtime-cli
COPY --from=builder-cli /out/pt /usr/local/bin/pt
COPY --from=builder-cli /out/hook-entry /usr/local/bin/hook-entry
USER nonroot:nonroot
ENTRYPOINT ["/usr/local/bin/pt"]
CMD ["--help"]

FROM gcr.io/distroless/cc-debian12:nonroot AS runtime-core
COPY --from=builder-core /build/target/release/dag-scheduler /usr/local/bin/dag-scheduler
# ... (one COPY per core-stream crate that has a binary)
USER nonroot:nonroot

FROM gcr.io/distroless/cc-debian12:nonroot AS runtime-ops
COPY --from=builder-ops /build/target/release/phenotype-tooling-observability /usr/local/bin/obs
COPY --from=builder-ops /build/target/release/sbom-gen /usr/local/bin/sbom-gen
COPY --from=builder-ops /build/target/release/release-cut /usr/local/bin/release-cut
COPY --from=builder-ops /build/target/release/ptx /usr/local/bin/ptx
USER nonroot:nonroot
```

### 2. deploy/docker-compose.prod.yml

```yaml
# deploy/docker-compose.prod.yml
# 3-stream production deployment. Each stream runs as a separate
# compose service with its own health-gate. The shared observability
# stack (Prometheus + Grafana) is defined here too so the roll-out
# can query the same /health endpoints the pt binary exposes.

services:
  cli:
    image: ghcr.io/kooshapari/phenotype-tooling/cli:${CLI_TAG}
    deploy:
      replicas: 4
      update_config:
        parallelism: 1
        order: start-first
        failure_action: rollback
    healthcheck:
      test: ["CMD", "/usr/local/bin/pt", "self", "ping"]
      interval: 30s
      timeout: 5s
      retries: 3
    environment:
      - PT_METRICS_PORT=9090
      - PT_HEALTH_PORT=8080
      - PT_STREAM_CHANNEL=${CLI_CHANNEL}
    ports:
      - "9090:9090"
      - "8080:8080"

  core:
    image: ghcr.io/kooshapari/phenotype-tooling/core:${CORE_TAG}
    deploy:
      replicas: 2
    healthcheck:
      test: ["CMD", "/usr/local/bin/dag-scheduler", "--health"]
    environment:
      - PT_STREAM_CHANNEL=${CORE_CHANNEL}

  ops:
    image: ghcr.io/kooshapari/phenotype-tooling/ops:${OPS_TAG}
    deploy:
      replicas: 1
    healthcheck:
      test: ["CMD", "/usr/local/bin/obs", "--health"]
    environment:
      - OBS_PROMETHEUS_BIND=0.0.0.0:9100
      - OBS_HEALTH_BIND=0.0.0.0:8081

  prometheus:
    image: prom/prometheus:v2.55.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./rules:/etc/prometheus/rules:ro
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --web.enable-lifecycle

  grafana:
    image: grafana/grafana:11.3.0
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
```

### 3. deploy/health-gate.yml

The health-gate is a YAML file consumed by both `pt deploy` and the
canary-rollout workflow. It defines the SLOs that must hold during a
roll-out for the canary to be promoted to 100%.

```yaml
# deploy/health-gate.yml
# SLO burn-rate thresholds. Match the alert rules in
# observability/prometheus/phenotype-tooling.rules.yml.
cli:
  success_rate:
    min: 0.999          # must stay >= 99.9% during canary
    observation_window: 5m
  startup_p95:
    max_ms: 200
    observation_window: 5m
  error_budget_remaining:
    min_pct: 50         # if error budget is below 50%, abort roll-out
core:
  scheduler_lag:
    max_s: 30
  task_failure_rate:
    max: 0.01
ops:
  scrape_success_rate:
    min: 0.95
  sbom_validation_lag:
    max_s: 60

# Cross-stream constraints
promotion:
  strategy: canary
  canary_pct: 5
  observation_minutes: 10
  abort_on: ['slo_breach', 'budget_exhausted', 'healthcheck_failure']
  rollback_strategy: instant  # no graceful drain — SLO breach = revert
```

### 4. crates/phenotype-cli/src/deploy.rs — `pt deploy` subcommand

```rust
//! `pt deploy` — orchestrates the canary roll-out + health-gate check
//! for a single stream. Reads deploy/health-gate.yml, queries the
//! Prometheus endpoint for SLO compliance during the canary window,
//! promotes or aborts based on the health-gate rule, and emits a
//! structured roll-out report.

use anyhow::{anyhow, bail, Context, Result};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::time::Duration;

#[derive(Debug, Clone, Deserialize)]
pub struct DeployArgs {
    /// Stream to deploy: cli | core | ops
    #[arg(long)]
    pub stream: String,
    /// Target version tag (e.g. v0.3.0)
    #[arg(long)]
    pub tag: String,
    /// Health-gate config path
    #[arg(long, default_value = "deploy/health-gate.yml")]
    pub gate: PathBuf,
    /// Prometheus query endpoint
    #[arg(long, default_value = "http://localhost:9090")]
    pub prometheus: String,
    /// Dry-run: report what would happen without actually deploying
    #[arg(long)]
    pub dry_run: bool,
    /// Skip the canary phase (full deployment immediately)
    #[arg(long)]
    pub skip_canary: bool,
}

#[derive(Debug, Serialize)]
pub struct RolloutReport {
    pub stream: String,
    pub tag: String,
    pub started_at: chrono::DateTime<chrono::Utc>,
    pub completed_at: Option<chrono::DateTime<chrono::Utc>>,
    pub phase: Phase,
    pub slo_compliance: Vec<SloCheck>,
    pub decision: Decision,
    pub log: Vec<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
pub enum Phase { Canary, Promotion, Complete, Aborted }

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
pub enum Decision { Promote, Hold, Rollback }

#[derive(Debug, Clone, Serialize)]
pub struct SloCheck {
    pub slo: String,
    pub observed: f64,
    pub threshold: f64,
    pub compliant: bool,
}

pub async fn run(args: DeployArgs) -> Result<RolloutReport> {
    let gate = load_gate(&args.gate)?;
    let stream_gate = gate.stream_gate(&args.stream)
        .ok_or_else(|| anyhow!("no health-gate rule for stream {}", args.stream))?;

    let mut report = RolloutReport {
        stream: args.stream.clone(),
        tag: args.tag.clone(),
        started_at: chrono::Utc::now(),
        completed_at: None,
        phase: Phase::Canary,
        slo_compliance: Vec::new(),
        decision: Decision::Hold,
        log: Vec::new(),
    };
    report.log.push(format!("[{}] deploy started", report.started_at));

    // Phase 1: spin up canary population
    if !args.skip_canary {
        apply_canary(&args, &gate).await
            .context("canary phase failed")?;
        report.log.push("canary population deployed".into());

        // Phase 2: observe the health-gate for the configured window
        let observation = observe_gate(&args, stream_gate, &gate.promotion).await
            .context("health-gate observation failed")?;
        report.slo_compliance = observation.checks.clone();
        report.decision = observation.decision;

        match observation.decision {
            Decision::Promote => {
                report.phase = Phase::Promotion;
                apply_promotion(&args, &gate).await?;
                report.log.push("canary promoted to 100%".into());
            }
            Decision::Hold => {
                report.phase = Phase::Aborted;
                report.log.push("health-gate held roll-out".into());
                bail!("health-gate held roll-out for stream {}", args.stream);
            }
            Decision::Rollback => {
                report.phase = Phase::Aborted;
                apply_rollback(&args).await?;
                report.log.push("rolled back to previous version".into());
                bail!("SLO breach during canary — rolled back");
            }
        }
    } else {
        apply_promotion(&args, &gate).await?;
        report.log.push("promoted directly (canary skipped)".into());
    }

    report.completed_at = Some(chrono::Utc::now());
    report.phase = Phase::Complete;
    Ok(report)
}
```

### 5. .github/workflows/deploy.yml — manual prod deployment

```yaml
name: deploy
on:
  workflow_dispatch:
    inputs:
      stream:
        description: 'Release stream to deploy'
        required: true
        type: choice
        options: [cli, core, ops]
      tag:
        description: 'Target tag (e.g. v0.3.0)'
        required: true
        type: string
      skip_canary:
        description: 'Skip the canary phase'
        required: false
        type: boolean
        default: false
      dry_run:
        description: 'Dry-run (report only)'
        required: false
        type: boolean
        default: false

permissions:
  contents: read
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: swatinem/rust-cache@v2

      - name: Build stream image
        run: |
          docker build \
            --target runtime-${{ inputs.stream }} \
            --tag ghcr.io/kooshapari/phenotype-tooling/${{ inputs.stream }}:${{ inputs.tag }} \
            --build-arg STREAM=${{ inputs.stream }} \
            .

      - name: Push image
        if: ${{ !inputs.dry_run }}
        run: |
          echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker push ghcr.io/kooshapari/phenotype-tooling/${{ inputs.stream }}:${{ inputs.tag }}

      - name: Run pt deploy
        if: ${{ !inputs.dry_run }}
        run: |
          cargo run -p phenotype-cli -- deploy \
            --stream ${{ inputs.stream }} \
            --tag ${{ inputs.tag }} \
            ${{ inputs.skip_canary && '--skip-canary' || '' }} \
            ${{ inputs.dry_run && '--dry-run' || '' }}
        env:
          CLI_TAG: ${{ inputs.tag }}
          CLI_CHANNEL: stable
          GRAFANA_ADMIN_PASSWORD: ${{ secrets.GRAFANA_ADMIN_PASSWORD }}

      - name: Upload rollout report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: rollout-${{ inputs.stream }}-${{ inputs.tag }}
          path: rollout-report.json
```

### 6. .github/workflows/canary-rollout.yml — scheduled auto-canary

Runs weekly on Monday 09:00 UTC. Picks the latest stable-channel
version from the WP-28 channel-manifest.json, deploys it as a 5%
canary, observes the health-gate for 10 minutes, then promotes or
rolls back automatically.

```yaml
name: canary-rollout
on:
  schedule:
    - cron: '0 9 * * 1'  # Mondays 09:00 UTC
  workflow_dispatch:

permissions:
  contents: read
  id-token: write

jobs:
  canary:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        stream: [cli, core, ops]
    steps:
      - uses: actions/checkout@v4

      - name: Read channel manifest
        id: manifest
        run: |
          CHANNEL=$(jq -r '.streams["${{ matrix.stream }}"].channels.stable' .github/channel-manifest.json)
          TAG=$(jq -r '.streams["${{ matrix.stream }}"].tags[$CHANNEL]' .github/channel-manifest.json)
          echo "tag=$TAG" >> $GITHUB_OUTPUT

      - name: Build canary image
        run: |
          docker build \
            --target runtime-${{ matrix.stream }} \
            --tag ghcr.io/kooshapari/phenotype-tooling/${{ matrix.stream }}:${{ steps.manifest.outputs.tag }}-canary \
            .

      - name: Push canary image
        run: |
          echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker push ghcr.io/kooshapari/phenotype-tooling/${{ matrix.stream }}:${{ steps.manifest.outputs.tag }}-canary

      - name: Deploy canary + observe
        run: |
          cargo run -p phenotype-cli -- deploy \
            --stream ${{ matrix.stream }} \
            --tag ${{ steps.manifest.outputs.tag }}-canary \
            --gate deploy/health-gate.yml \
            --prometheus http://prometheus:9090

      - name: Notify Slack
        if: always()
        uses: slackapi/slack-github-action@v1.27.0
        with:
          payload: |
            {
              "text": "Canary roll-out for ${{ matrix.stream }}@${{ steps.manifest.outputs.tag }}: ${{ job.status }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Acceptance criteria

- [ ] `docker build --target runtime-cli` produces a working cli-stream image
- [ ] `docker build --target runtime-core` produces a working core-stream image
- [ ] `docker build --target runtime-ops` produces a working ops-stream image
- [ ] `docker compose -f deploy/docker-compose.prod.yml up` boots the full 3-stream stack
- [ ] `pt deploy --stream cli --tag v0.3.0 --dry-run` reports the planned canary
- [ ] `pt deploy --stream cli --tag v0.3.0` rolls the cli stream forward
- [ ] SLO breach during canary auto-aborts and rolls back
- [ ] Cross-stream health-gate constraints (cli success rate, core scheduler lag, ops scrape rate) all enforced
- [ ] Weekly canary-rollout.yml runs the canary and notifies Slack

## Rollout plan

| Week | Action |
|------|--------|
| 1 | Manual deploys only via `workflow_dispatch`. Health-gate in shadow mode (reports only, no abort). |
| 2 | Health-gate enforce mode. Canary 5%, observation 10 min. Auto-rollback on SLO breach. |
| 3 | Weekly auto-canary on Monday 09:00 UTC for all 3 streams. |
| 4+ | Add per-stream promotion strategies (canary → blue-green for core stream, etc.). |