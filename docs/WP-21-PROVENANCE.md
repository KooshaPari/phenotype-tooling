# WP-21: In-Toto Provenance Attestation Per Binary

**Status:** implemented in `signed-release.yml` (WP-20 commit `31680a49` + WP-21 patch)

## Why

Every release binary should carry **SLSA-build-level-3 provenance** — a tamper-evident attestation describing exactly which source revision, build command, and CI environment produced the artifact. Without provenance, a downstream consumer can't verify that a binary was built from the source they expect.

Phase 3 (WP-12) shipped SLSA provenance for the `release-artifacts` archive as a single bundled attestation. WP-21 extends that to **per-binary provenance** so each `.exe` has its own attestation attached to the GitHub Release.

## What ships

| File | Purpose |
|---|---|
| `.github/workflows/signed-release.yml` | Added `actions/attest-build-provenance@v1` step per binary |
| `docs/WP-21-PROVENANCE.md` | This document |

## Provenance format

```jsonl
{
  "_type": "https://in-toto.io/Statement/v0.1",
  "predicateType": "https://slsa.dev/provenance/v0.2",
  "subject": [{"name": "phenotype-cli-x86_64-unknown-linux-gnu.exe", "digest": {"sha256": "..."}}],
  "predicate": {
    "buildType": "https://github.com/actions/workflow-build/v1",
    "builder": {"id": "https://github.com/KooshaPari/phenotype-tooling/actions/runs/28684600945"},
    "invocation": {
      "configSource": {"uri": "git+https://github.com/KooshaPari/phenotype-tooling@refs/tags/v0.2.0", "digest": {"sha1": "350491a0"}},
      "entryPoint": ".github/workflows/signed-release.yml",
      "arguments": ["v0.2.0", "keyless"]
    },
    "materials": [{"uri": "git+https://github.com/KooshaPari/phenotype-tooling", "digest": {"sha1": "350491a0"}}]
  }
}
```

Each binary in `target/release/` gets its own `.intoto.jsonl` attestation, uploaded to the GitHub Release as `&lt;binary-name&gt;.intoto.jsonl`.

## Consumer verification

```bash
# Download binary + attestation
gh release download v0.2.0 phenotype-cli-x86_64-unknown-linux-gnu.exe
gh release download v0.2.0 phenotype-cli-x86_64-unknown-linux-gnu.exe.intoto.jsonl

# Verify with slsa-verifier
slsa-verifier verify-artifact phenotype-cli-x86_64-unknown-linux-gnu.exe \
  --provenance-path phenotype-cli-x86_64-unknown-linux-gnu.exe.intoto.jsonl \
  --source-uri github.com/KooshaPari/phenotype-tooling
```

## Acceptance criteria

- [ ] Each binary in v0.2.0 release has an `.intoto.jsonl` attestation
- [ ] `slsa-verifier verify-artifact` returns **PASSED** for at least 3 sample binaries
- [ ] Provenance `subject[0].digest.sha256` matches the binary's actual SHA-256
- [ ] Provenance `predicate.invocation.configSource.digest.sha1` matches the release tag's commit SHA