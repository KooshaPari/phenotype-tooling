# phenotype-actions

Reusable GitHub Actions workflows and composite actions for the
[Phenotype](https://github.com/kooshapari) ecosystem.

Centralising the CI gate definitions here means a single fix lands in
every consumer repo at once, and every Phenotype crate is held to the
same supply-chain standard.

## What's inside

| Path | Kind | Purpose |
| --- | --- | --- |
| `.github/workflows/rust-ci.yml` | `workflow_call` | cargo fmt / check / clippy / test on a pinned toolchain |
| `.github/workflows/cargo-deny.yml` | `workflow_call` | License + advisory + bans + sources policy gate |
| `.github/workflows/cargo-audit.yml` | `workflow_call` | RustSec advisory DB cross-check, weekly schedule |
| `.github/workflows/coverage.yml` | `workflow_call` | cargo-tarpaulin + Codecov upload, configurable threshold |
| `.github/workflows/scorecard.yml` | `workflow_call` | OSSF Scorecard SARIF upload to code-scanning |
| `actions/pin-sha` | composite | Lookup the canonical pinned SHA for known third-party actions |
| `templates/concurrency.yml` | snippet | Recommended `concurrency:` block for consumer workflows |
| `templates/concurrent-prs.yml` | snippet | Full example wiring up all five workflows |

## Quick start

```yaml
# .github/workflows/ci.yml in your repo
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

permissions:
  contents: read

jobs:
  rust-ci:
    uses: kooshapari/phenotype-actions/.github/workflows/rust-ci.yml@v0.1.0
    with:
      toolchain: "stable"
      cache-key-prefix: "myrepo-rust"

  cargo-deny:
    uses: kooshapari/phenotype-actions/.github/workflows/cargo-deny.yml@v0.1.0

  cargo-audit:
    uses: kooshapari/phenotype-actions/.github/workflows/cargo-audit.yml@v0.1.0

  coverage:
    uses: kooshapari/phenotype-actions/.github/workflows/coverage.yml@v0.1.0
    with:
      min-coverage: 70
    secrets:
      codecov-token: ${{ secrets.CODECOV_TOKEN }}
```

## Versioning

Tag the repo with semver. Consumers pin to a tag (`@v0.1.0`) — never
to `@main` — so a breaking change to a workflow input cannot silently
break a build.

## Concurrency policy

Every consumer workflow **must** include a `concurrency:` block:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

Rationale: cancel superseded PR runs to save CI minutes, but **never**
cancel a run on `main` — the queued run is the source of truth for the
release.

## Permission policy

Every consumer workflow **must** declare a `permissions:` block at the
top level, scoped to the smallest set of capabilities it actually
needs. The default is `contents: read`.

## Adding a new workflow

1. Add the new file under `.github/workflows/`.
2. Use `on: workflow_call:` (not `on: push` or `on: pull_request`).
3. Declare typed `inputs:` and `outputs:`.
4. Declare any `secrets:` (never pass `secrets.*` implicitly).
5. Set `permissions:` to the minimum required.
6. Update this README and tag a new release.

## Security

See [SECURITY.md](SECURITY.md).
