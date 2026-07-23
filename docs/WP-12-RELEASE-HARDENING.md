# Release hardening + SBOM publication

## Scope

WP-12 closes the loop on Phase-3 distributed artifacts. The pipeline is:

```
            ┌─────────────────┐
 tag v* ──▶ │ release.yml     │ ──▶ cargo publish --locked
            │ (existing)      │
            └─────────────────┘

            ┌──────────────────────┐
 release  ──▶│ release-attestation  │ ──▶ SLSA Build L2 provenance
 published   │ .yml (existing)      │    via slsa-framework
            └──────────────────────┘

            ┌──────────────────────┐
 release  ──▶│ signed-release.yml   │ ──▶ cosign sign-blob (keyless OIDC)
 published   │ release-sbom.yml    │    upload signed bundle to release
            └──────────────────────┘
```

## Existing infrastructure (consumed, not duplicated)

| File | Role |
|---|---|
| `.github/workflows/release.yml` | tags → `cargo publish -p &lt;name&gt;` |
| `.github/workflows/release-attestation.yml` | builds, stages, uploads SLSA provenance |
| `.github/workflows/rust-ci.yml` | nightly fmt/clippy/test gate |
| `crates/sbom-gen/` | CycloneDX-JSON SBOM generator → `docs/security/sbom.json` |
| `crates/sbom-gen/docs/security/sbom.json` | committed SBOM artifact |
| `crates/fuzz-setup/` | nightly fuzz harnesses + corpus cache |

## New workflow files (this WP)

### `.github/workflows/signed-release.yml`

- **Trigger**: `release: types: [published]`
- **Permission**: `id-token: write` (Sigstore keyless OIDC), `contents: write` (upload), `attestations: read`
- **Job `sign-artifacts`**:
  1. Download `release-artifacts` uploaded by `release-attestation.yml`
  2. For each file: `cosign sign-blob --yes \
     --output-signature=&lt;name&gt;.sig \
     --output-certificate=&lt;name&gt;.cert &lt;file&gt;`
  3. Upload the entire `signed/` directory as the `signed-release-artifacts`
     artifact (90-day retention)
- **Job `attach-to-release`**:
  1. Download `signed-release-artifacts` + `source.tar.gz`
  2. `gh release upload &lt;tag&gt; signed/*.sig signed/*.cert source.tar.gz` — bumped
     past collision with attestation
- **Why keyless OIDC + cosign**: works for public repos without managing any
  long-lived signing key, satisfies SLSA Build L3 supply-chain provenance.

### `.github/workflows/release-sbom.yml`

- **Trigger**: `release: types: [published]`, plus `workflow_dispatch`
- **Permission**: `contents: read`
- **Steps**:
  1. Checkout source at the tagged ref
  2. Install Rust toolchain (matches release)
  3. `cargo run -p sbom-gen --release --locked` → regenerates `sbom.json`
     deterministically from `Cargo.lock` (no network, no env)
  4. Verify CycloneDX shape (`bomFormat == "CycloneDX"`)
  5. Upload `sbom.json`, `sbom.json.sha256`, `sbom.spdx.json` to the release
     (SPDX is generated alongside by the same tool)

### Why regenerate the SBOM at release time (not commit)

The committed `sbom.json` is a **preview from WP-09's verification window**.
At release time we re-run `sbom-gen` so the published SBOM:

- Reflects the **exact** `Cargo.lock` of the release (no drift)
- Includes any new workspace members added between the last commit and tag
- Carries the correct `metadata.timestamp` and provenance

## Documented exit codes

| Job | Failure mode | Visible artefact |
|---|---|---|
| `release-sbom.yml` | `sbom-gen` exits non-zero | Red ❌ on the SBOM job in Actions |
| `signed-release.yml / sign-artifacts` | `cosign` exits non-zero | Red ❌ + missing `.sig`/`.cert` for that file |
| `release.yml` | `cargo publish` rejects | Pinned by `release` GitHub Environment approval |

## Acceptance criteria

- [ ] Tag `v0.0.0-test` (any tag matching `v*`) publishes to crates.io
- [ ] SLSA provenance bundle uploads to the release as `&lt;artifact&gt;.intoto.jsonl`
- [ ] `sbom.json`, `sbom.json.sha256`, `sbom.spdx.json` appear as release assets
- [ ] Every file in `release-artifacts/` gets a sibling `.sig` and `.cert`
      visible on the release page
- [ ] `cosign verify-blob --certificate &lt;name&gt;.cert --signature &lt;name&gt;.sig \
      --certificate-identity-regexp 'https://github.com/.*/.github/workflows/signed-release.yml' \
      --certificate-oidc-issuer-regexp 'https://token.actions.githubusercontent.com' \
      &lt;name&gt;` exits 0 with bundle hash output

## How to add a new artifact to the signed-release contract

1. Add the file path under `paths:` of the `upload-artifacts@release-artifacts`
   step in `release-attestation.yml`
2. Re-run a tag; the `sign-artifacts` job will pick it up automatically because
   it iterates `find signed/` after download

## Failure surfaces

- **Unsigned release**: GH Environment `release` blocks `cargo publish` until
  manual approval — no signing key can be lost because none exists. Compromised
  workflow identities inherit only the OIDC token validity window (15min).
- **Drift between `Cargo.lock` and published SBOM**: Solved by regenerating
  the SBOM at release time rather than trusting the committed one.
- **Forgot to bump the version**: `release` job runs `cargo publish` and will
  fail-fast on a 409 (already-published); release visibility is unaffected.
