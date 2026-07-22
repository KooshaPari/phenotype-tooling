# WP-22 — SBOM Diff Policy + Dependency License Check

## Goal

Block PRs that introduce new high/critical CVEs or license violations in
their dependency tree.

## Two Workflows

### `.github/workflows/sbom-diff.yml`

Triggered on every PR to main. Steps:

1. checkout
2. setup-rust stable + cache
3. install cargo-cyclonedx, cargo-deny
4. Generate SBOM from Cargo.lock (`cargo cyclonedx --format json`)
5. Download the SBOM from the latest successful `main` build
   (artifact from release-sbom.yml or a synthesized version)
6. Diff: parse both SBOMs, extract `(name, version)` tuples per component,
   find packages new-to-this-PR.
7. For each new package, query OSV.dev (https://api.osv.dev/v1/query) for
   known vulnerabilities.
8. For each vuln with `severity == HIGH | CRITICAL`:
   - Leave a PR review comment listing the vuln
   - Set the `sbom-policy / high-severity` check to `failure`
9. For packages with no vuln but new license terms that don't match the
   allow-list (MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, MPL-2.0,
   CC0-1.0, Unlicense):
   - Same as above with `sbom-policy / license` check

The check name is `sbom-policy` so branch-protection can require it.

### `.github/workflows/license-check.yml`

A second copy of just the license check, run on every PR with the
`required-status-checks` context name `license`. This is the WP-22 surface
*separate* from SBOM scanning so the two failures don't collapse.

## Allow-list

```
allow_licenses = [
    "MIT",
    "Apache-2.0",
    "Apache-2.0 OR MIT",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "MPL-2.0",
    "CC0-1.0",
    "Unlicense",
    "Zlib",
]
```

Anything outside this allow-list fails `license` check.

## Override Path

If a new dependency must be added that has a CRITICAL vuln or non-allowed
license:
1. PR author adds `# license-override: &lt;justification&gt;` to the commit body
2. CODEOWNER (@KooshaPari) review overrides the `license` check
3. PR auto-merges after CODEOWNER override

## Acceptance Criteria

- PRs adding a dep with `tokio = "0.2"` (no license override) → `license`
  check fails on the MIT license policy miss → branch protection blocks
  merge
- PRs adding `openssl = "0.10.55"` (CVE-2023-XXX) → `sbom-policy` check
  fails on the severity block → branch protection blocks merge
- After CODEOWNER override: PR merges, override appears in release notes

## Files

| File | Purpose |
|---|---|
| `.github/workflows/sbom-diff.yml` | SBOM diff + vuln check (PR trigger) |
| `.github/workflows/license-check.yml` | License-only check (PR trigger) |
| `scripts/sbom_diff.py` | SBOM comparison logic + OSV.dev query |
| `scripts/license_check.py` | License allow-list enforcement |
| `LICENSE_ALLOWLIST.toml` | Centralised allow-list config |
| `docs/WP-22-SBOM-DIFF.md` | This doc |

## Relationship to Other WPs

- **WP-12** (signed release): SBOM is generated and attached
- **WP-20** (KMS signing): vuln disclosure surface for the signed SBOM
- **WP-23/24** (coverage + mutation gates): sibling PR gates

## Status

Workflow files drafted in the WP-22 commit; final rollout pending
branch-protection wiring for `sbom-policy` and `license` required
checks (separate from WP-23/24's coverage/mutation gates).
