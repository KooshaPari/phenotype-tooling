# Threat Model

> **Source of truth:** phenotype-dep-guard (Python 3.12+ supply-chain guard tool distributed as a Click CLI `dep-guard`)

## Scope

This template models a Python 3.12+ supply-chain guard tool distributed as a Click CLI (`dep-guard`) that ingests dependency manifests (TOML/PyYAML/lockfiles), resolves package metadata via PURL, and emits pass/fail verdicts to CI gates. The model is STRIDE-classified and applies to the CLI invocation surface, the local resolver/auditor core (`src/phenotype_dep_guard/`), the network egress to advisory registries, and the JSON report artifacts persisted to the consuming repo's audit trail.

## Assets (what we protect)

- **A1 — Verdict integrity:** the pass/fail signal a CI gate consumes; corruption here either silences a malicious dep or blocks a clean one.
- **A2 — Manifest inputs:** `pyproject.toml`, `requirements*.txt`, `poetry.lock`, `uv.lock`, `Pipfile.lock` read from the target repo; trusted only insofar as their source tree is trusted.
- **A3 — Resolver/auditor core:** pure-Python logic that parses manifests, constructs PURLs, evaluates policy rules, and writes JSON scorecards.
- **A4 — Outbound channels:** `httpx` calls to advisory feeds (OSV, GHSA, PyPI JSON, internal mirror); the egress credentials, tokens, and proxy config in `~/.config/phenotype/` or env.
- **A5 — Local policy bundle:** the rule packs, allow/deny lists, and severity thresholds shipped with the tool or fetched as signed bundles.
- **A6 — Audit artifacts:** `audit_scorecard.json` and the `docs/security/`-style reports written next to the target repo.
- **A7 — Distribution channel:** the wheel/sdist, the GitHub release tag, the `reusable-dep-guard` workflow, and the package signing key.

## STRIDE Threats

- **Spoofing:** an attacker forges an advisory response (DNS hijack on the registry mirror, or a malicious `packageurl-python` resolver returning a PURL for a typosquatted package) so the guard endorses a backdoored dep. Mitigations: pin registry endpoints, verify TLS with system roots, validate PURL authority against an allowlist, and require Sigstore/PEP 740 attestations for any package the tool recommends.
- **Tampering:** manifest inputs are read with `toml`/`pyyaml` — a crafted manifest with anchor-bomb YAML, deep nesting, or pathological TOML can crash the parser or smuggle values into the policy engine. Mitigations: use safe loaders, set hard size and nesting limits, and reject manifests that mutate the tool's own rule set.
- **Repudiation:** a CI run that fails-open could be silently re-run with a relaxed policy and the evidence discarded. Mitigations: append-only JSONL of verdicts, content-hash the scorecard, sign the artifact with the runner's key, and require the gate job to publish a `gh attestation` for the report SHA.
- **Information disclosure:** the resolver logs PURLs, versions, and (in verbose mode) full HTTP request bodies including auth headers from `python-dotenv`. Mitigations: scrub Authorization/Cookie headers before logging, redact env-var values echoed in tracebacks, and gate `rich`-pprint output behind `--debug` with a security redaction filter.
- **Denial of service:** a malicious manifest with millions of dependencies, or a recursive `[tool.uv.sources]`, can pin CPU/memory and stall CI. Mitigations: bounded worker pool, per-run wall-clock and RSS limits, and refuse to resolve manifest graphs that exceed N nodes before producing a partial verdict.
- **Elevation of privilege:** the CLI runs inside CI and inherits the runner's network and filesystem rights. A confused-deputy attack via `--policy-url` or `--registry-override` could let an attacker load arbitrary Python from the policy bundle. Mitigations: refuse to load policy from HTTP unless the response is signature-verified, and run the resolver in a least-privilege sandbox.

## Residual risk & revision cadence

With the above mitigations, the dominant residual risks are (a) zero-day supply-chain compromise of an upstream advisory feed the tool trusts, (b) policy-author compromise of a maintainer with release-signing rights, and (c) a permissive local config in `.phenotype-dep-guard.toml` that downgrades severity. These are tracked, not eliminated. No residual rated *Critical* may ship to `main`; any *High* must have a documented compensating control and a tracked issue. The threat model is re-evaluated whenever any of the following change: (i) a new outbound registry is added, (ii) the policy bundle format is bumped, (iii) the CLI gains a new subcommand, or (iv) a CVE is published against any direct or transitive dependency. This document is reviewed **quarterly** by the supply-chain security owner, **on every release** of the tool (minor and major), and **within 72 hours** of any advisory affecting a direct or transitive dependency.
