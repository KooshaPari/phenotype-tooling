# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in **PhenoDevOps**, please report it privately via GitHub's security advisories:

- https://github.com/KooshaPari/PhenoDevOps/security/advisories/new

Please do **not** open a public issue for security reports. We will acknowledge receipt within 72 hours and provide a remediation timeline based on severity.

## Supported Versions

This repository is currently in **drain** per `plans/2026-06-18-devhex-port-v1.md` and is being archived once its content has migrated to its canonical homes (see `AGENTS.md` for the stage table).

| Branch / Tag | Supported |
|---|---|
| `main` (current drain target) | Best-effort security fixes only |
| Older branches / historical tags | None — please upgrade |

While in drain, this repo is read-mostly: critical CVE fixes may be backported at the maintainers' discretion, but new feature work is not accepted.

## Scope

This policy covers the source trees that still ship from `KooshaPari/PhenoDevOps` itself. Specifically:

- `agent-devops-setups/` — Python policy federation + shell scripts (Stage 1 → `phenotype-ops`)
- Documentation under `docs/`

Sub-trees that are scheduled for deletion in Stages 2–4 of the drain (e.g. `crates/forgecode-core/`, `crates/phenotype-router-monitor/`, `crates/bifrost-routing*/`) are **out of scope** — report issues against their canonical home instead:

- `AgilePlus` (https://github.com/KooshaPari/AgilePlus)
- `HexaKit` (https://github.com/KooshaPari/HexaKit)
- `phenotype-ops` (https://github.com/KooshaPari/phenotype-ops)

## Coordinated Disclosure

We follow a coordinated disclosure model. Once a fix is available and deployed, we will publish a public advisory crediting the reporter (unless anonymity is requested).

## Security Tooling

This repository runs the following automated security checks on every push and weekly cron:

| Workflow | What it does |
|---|---|
| `.github/workflows/audit.yml` | `cargo audit` (RustSec) + `npm audit` (JS/TS) + `pip-audit` (Python) |
| `.github/workflows/deny.yml` | `cargo-deny` (licenses / bans / advisories / sources) + `go mod verify` + `govulncheck` |
| `.github/workflows/codeql.yml` | CodeQL static analysis |
| `.github/workflows/trufflehog.yml` | Secret scanning |
| `.github/workflows/trivy-scan.yml` | Container/filesystem CVE scan |
| `.github/workflows/snyk-scan.yml` | Snyk SCA |
| `.gitleaks.toml` (root) | Pre-commit secret detection |

Dependency updates are managed by Dependabot (`.github/dependabot.yml`).

## Contact

- GitHub Security Advisories: https://github.com/KooshaPari/PhenoDevOps/security/advisories/new
- Maintainer: @KooshaPari
- Response SLA: 72 hours for acknowledgement, severity-driven remediation timeline thereafter