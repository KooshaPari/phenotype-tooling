# WP-27 — SBOM Attestation Chain

## Goal

Every CycloneDX SBOM published by WP-12 / WP-22 becomes
**independently verifiable**: signed with cosign keyless OIDC,
chained to the binary release it describes, and tied to the source
commit via in-toto provenance.

```
WP-12 sbom-gen produces sbom.json (CycloneDX 1.5 JSON, ~90 KB)
   ↓
WP-22 sbom-diff computes the diff vs previous release
   ↓
WP-27 sign_sbom_attestation.py (NEW)
   1. Hashes sbom.json (sha256)
   2. Wraps it in an in-toto attestation envelope
      {
        "payloadType": "application/vnd.in-toto+json",
        "payload": {
          "predicateType": "https://cyclonedx.org/evidence/bom",
          "predicate": { ... sbom contents ... }
        },
        "signatures": []
      }
   3. cosign sign-blob attaches a keyless signature
   4. Rekor uploads the signature to the transparency log
   5. Emits sbom.json.intoto.jsonl + sbom.json.sig + sbom.json.cert
   6. Posts the chain to the GitHub release alongside sbom.json
```

The chain: **sbom.json → intoto envelope → cosign sig → rekor entry → OIDC issuer**.
Verifiers run `cosign verify-blob --certificate-identity <release-url>` to
confirm the SBOM was signed by the same release CI run.

## Deliverables

| File | Purpose |
|---|---|
| `scripts/sign_sbom_attestation.py` | Wrap + sign + upload pipeline |
| `.github/workflows/release-sbom-attestation.yml` | Triggered after `release-sbom.yml` succeeds |

## Trigger

`on.workflow_run` on `release-sbom.yml` completion with `conclusion=success`.
Idempotent: re-runs overwrite the same `.sig`/`.cert`/`.intoto.jsonl` triple.

## Consumer Verification

```bash
# Download sbom + signature from release assets
gh release download v0.3.0 --pattern 'sbom*'

# Verify signature against the release CI's OIDC identity
cosign verify-blob \
  --certificate-identity-regexp 'https://github.com/KooshaPari/phenotype-tooling' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  --signature sbom.json.sig \
  --certificate sbom.json.cert \
  sbom.json
```

## Acceptance Criteria

1. Every v0.3.0+ release ships with sbom.json + sbom.json.intoto.jsonl + sbom.json.sig + sbom.json.cert
2. `cosign verify-blob` succeeds with the GitHub OIDC issuer pattern
3. The in-toto envelope contains the full CycloneDX SBOM as the predicate body
4. Rekor entry retrievable from `https://rekor.sigstore.dev/api/v1/log/entries/<hash>`
5. Failure modes (signing error, Rekor upload error) produce a clear GH Actions annotation, not silent skip