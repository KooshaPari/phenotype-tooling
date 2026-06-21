# Security Policy

## Reporting a Vulnerability

To report a security vulnerability in **PhenoMCP**, please use **one** of the following private channels:

- **Email:** kooshapari@kooshapari.com
- **GitHub Security Advisories:** open a [private security advisory](https://github.com/KooshaPari/PhenoMCP/security/advisories/new) on this repository

> **Do NOT open a public issue for security vulnerabilities.**
> Public disclosure before a fix is available gives attackers a head start on
> every downstream user.

Please include, where possible:

1. A clear description of the vulnerability and its impact
2. Steps to reproduce or a proof-of-concept
3. Affected versions / commit SHAs
4. Your name / handle for the public acknowledgement (unless you prefer to stay anonymous)

## Response Timeline

We follow a coordinated disclosure model and aim for the following SLAs:

| Stage | Target |
|-------|--------|
| **Initial acknowledgement** | within **3 business days** |
| **Triage & severity assessment** | within **7 business days** |
| **Patch for critical / high severity** | within **30 days** |
| **Patch for medium / low severity** | within **90 days** |
| **Public disclosure** | after the patch is released (or sooner by mutual agreement) |

If we cannot meet these targets we will keep you informed of progress and a revised ETA.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.x.x   | :white_check_mark: |
| 1.x.x   | :white_check_mark: |

Older releases may receive patches at the maintainers' discretion; please open an advisory to ask.

## Scope

The following are **in scope**:

- The `pheno-mcp` binary and its workspace crates under `crates/`
- The Python bindings under `python/`
- The TypeScript / Node bindings under `ts/` (if present)
- The Go SDK under `go/` (if present)
- Mojo bindings under `mojo/` (if present)
- WASI / WebAssembly builds under `wasi/` (if present)
- FFI surface under `ffi/` (if present)
- CI / release automation in `.github/`
- Documentation that ships with a release

The following are **out of scope**:

- Vulnerabilities in third-party services we do not own
- Issues requiring physical access to a user's device
- Social-engineering attacks against maintainers
- Reports from automated scanners without a PoC demonstrating real impact

## Continuous Security Controls

PhenoMCP ships with automated supply-chain and vulnerability controls:

- **[`audit.yml`](../../workflows/audit.yml)** — `cargo audit`, `npm audit`,
  `pip audit` (PyPI via OSV), and Trufflehog verified-secrets scan, scheduled weekly.
- **[`deny.yml`](../../workflows/deny.yml)** — `cargo-deny` (license / ban /
  source / advisory policy from `deny.toml`) and `govulncheck` + `go mod verify`
  for the Go SDK, scheduled weekly.
- **[`dependabot.yml`](../../dependabot.yml)** — weekly automated updates for
  `cargo`, `npm`, `gomod`, `pip`, and `github-actions` ecosystems.
- **[`sbom.yml`](../../workflows/sbom.yml)** — CycloneDX SBOM is produced on every release.
- **[`scorecard.yml`](../../workflows/scorecard.yml)** — OpenSSF Scorecard is reported per push to `main`.

## Known Security Advisories

Published advisories are tracked on the
[GitHub Security Advisories tab](https://github.com/KooshaPari/PhenoMCP/security/advisories)
for this repository. There are no known unpatched critical vulnerabilities at this time.

## Acknowledgements

We are grateful to the security community. Reporters who follow this policy
and allow responsible disclosure will be credited in the release notes (unless
they prefer to remain anonymous).