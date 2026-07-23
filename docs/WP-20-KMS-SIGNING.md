# WP-20 — KMS-Backed Release Signing

## Purpose

Replace the keyless OIDC signing provider used since WP-12 with a
**long-lived KMS-backed key**. Keyless OIDC relies on a transient
Sigstore root key each release; a KMS key is owned by the project
and remains stable across releases, enabling replay-detection
windows and 7-year retention per SLSA Build L3.

## Why Now

| Concern | Keyless OIDC (today) | KMS-backed (WP-20) |
|---|---|---|
| Replay window | Per-run, then expires | Stable 1y+ |
| Signer identity | `https://github.com/...` | `phenotype-tooling@kms.cosign.sigstore.dev` |
| Re-issuance | Replay-protection = time-limited | Replay-protection = key revocation |
| Audit chain | OIDC only | KMS audit log + Sigstore transparency log |
| Compliance | SLSA Build L2 | SLSA Build L3 (long-lived identity) |

## Architecture

```
.github/workflows/signed-release.yml (workflow_dispatch variant)
  ─────────────────────────────────────────────────────────────
  inputs:
    tag: "v0.3.0"
    signer: keyless | kms    # default keyless for backward-compat
  ─────────────────────────────────────────────────────────────

  if signer == kms:
    - id-token: write         # still need OIDC for Sigstore federated identity
    - env.KMS_KEY_ID: ${{ vars.PT_KMS_KEY }}  # GitHub Actions variable
    - uses: sigstore/kms-signing-action@v1  # sign via KMS, get signature
    - uploads .sig/.cert/.bundle as release assets
```

The `keyless` path (the default) keeps using cosign's built-in
keyless OIDC for compatibility with v0.2.0 signatures. The `kms`
path uses a Sigstore KMS-signing key registered at
[github.com/phenotype-tooling/kms-keys](github.com/phenotype-tooling/kms-keys).

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/signed-release.yml` | Workflow updated to dispatch on `signer: keyless\|kms` |
| `.github/CODEOWNERS` | Adds `phenotype-tooling/kms-keys` owner approval rule |
| `docs/WP-20-KMS-SIGNING.md` | This document |

## Configuration

1. **Generate KMS key**: `cosign sign-blob-with-kms --output-certificate cert.pem --output-signature sig.bin` against a `kms://conformancekey` URI registered in [accounts.google.com](accounts.google.com) / Google Cloud KMS / HashiCorp Vault transit.

2. **Register the key with Sigstore**: browse to `https://rekor.tlog.dev/?publicKey=&lt;base64&gt;` to publish the public key in the Sigstore transparency log.

3. **Store the KMS key ref** as a GitHub Actions **variable** (not secret — it's a URI not a key):
   ```
   gh variable set PT_KMS_KEY --repo KooshaPari/phenotype-tooling \
     --body "gcp-kms://projects/phenotype-tooling/locations/global/keyRings/release/cryptoKeys/v1"
   ```

## Acceptance Criteria

1. Manual dispatch with `signer: kms` on `v0.3.0` produces .sig files signed by the KMS key
2. The KMS key fingerprint appears in `cosign verify-blob` output
3. Re-signing the same blob within the 1y replay window produces **identical** signatures — proving replay protection works
4. The KMS key appears in [`rekor.tlog.dev`](https://rekor.tlog.dev) public search
5. Audit log proves the KMS sign happened (Cloud KMS or Vault audit entry)

## Migration Plan

1. **Shadow mode (2 weeks)**: produce KMS-signed .sig files alongside keyless ones; verify both verify against their respective identities
2. **Cutover**: flip signed-release.yml default to `signer: kms`
3. **Deprecate keyless**: tag the last keyless release; document the migration in CHANGELOG.md

## Why this WP matters

SLSA Build L3 requires a **non-forgeable, long-lived signer
identity**. Keyless OIDC satisfies L2 because the OIDC token ties
the signature to a GitHub Actions run, but the identity is
transient. KMS backing makes the identity durable, so a release
signed in 2026-12 is verifiable against the same identity in
2033-12 — required for any vendor that ships this codebase through
SLSA-compliant supply-chain attestation tooling.
