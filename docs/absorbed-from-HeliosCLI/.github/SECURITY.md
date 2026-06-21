# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in HeliosCLI, please report it
privately. **Do not** open a public GitHub issue, pull request, or
discussion for security-sensitive reports.

### How to report

Use **one** of the following channels (in order of preference):

1. **GitHub private vulnerability reporting**
   Navigate to the repository's *Security* tab → *Advisories* →
   *Report a vulnerability*. This routes directly to the maintainers
   without exposing details publicly.
2. **Email**
   Send a description, reproduction steps, and impact assessment to the
   address listed in the repository's `CODEOWNERS` `SECURITY` contact.
   If no email is published, open a draft GitHub Security Advisory
   instead.
3. **Coordinated disclosure**
   If you are a downstream consumer, distributor, or researcher who
   needs an NDA, indicate this in your initial report and we will
   follow up.

### What to include

To help us triage quickly, please include:

- The vulnerable component (crate, npm package, workflow, etc.) and
  commit SHA or release tag.
- A reproducible proof of concept (commands, payload, or test case).
- The impact class (RCE, privilege escalation, info disclosure, supply
  chain, etc.) and affected platforms.
- Whether the vulnerability is already known or publicly disclosed.
- Your preferred credit name (or "anonymous") for the advisory.

We acknowledge reports within **3 business days** and provide an
initial assessment within **10 business days**.

## Supported Versions

HeliosCLI follows semver for its public CLI surface and Cargo workspace.
Security patches are backported to:

| Version line | Supported          |
|--------------|--------------------|
| `main`       | ✅ Always patched  |
| Latest tag   | ✅ Critical & high |
| Older tags   | ❌ Best-effort only |

For the Rust workspace (`codex-rs/`) and the Node CLI
(`codex-cli/`), security advisories are published as GitHub Security
Advisories and listed in the release notes.

## Security Tooling

HeliosCLI runs the following automated security scans on every push,
pull request, and weekly schedule:

| Workflow              | Scope                                                |
|-----------------------|------------------------------------------------------|
| `audit.yml`           | `cargo audit`, `pnpm audit`, `pip-audit`            |
| `deny.yml`            | `cargo-deny` (advisories, bans, licenses, sources); `govulncheck` (Go) |
| `codeql.yml`, `codeql-rust.yml` | Static analysis (Rust + multi-language)     |
| `trivy-scan.yml`      | Filesystem + container image CVE scanning            |
| `snyk-scan.yml`       | Open-source dependency vulnerability scanning       |
| `sast-full.yml`, `sast-quick.yml` | Semgrep SAST                          |
| `leak-detection.yml`  | TruffleHog secret scanning                           |
| `zap-dast.yml`        | OWASP ZAP dynamic application security testing        |
| `scorecard.yml`       | OpenSSF Scorecard                                     |

Dependabot (`.github/dependabot.yml`) opens weekly PRs for Rust
(`cargo`), Node (`npm`), and GitHub Actions dependency updates.

## Threat Model Summary

The authoritative threat model lives in `THREAT_MODEL.md` (when present)
and is reviewed per release. Key assumptions:

- **Trusted user input**: command-line flags and configuration files
  in well-known locations (`~/.codex/`, `$XDG_CONFIG_HOME/codex/`,
  repository `.codex/`) are trusted.
- **Untrusted input**: file contents read by tools, network responses,
  shell tool outputs, and MCP server responses are treated as
  untrusted and sandboxed.
- **Sandbox boundary**: macOS sandbox-exec, Linux Landlock+seccomp,
  Windows token-restricted job; failures default to **fail-closed**.
- **Supply chain**: dependencies pinned via `Cargo.lock`, `pnpm-lock.yaml`,
  and `requirements*.txt` hashes; `cargo-deny` enforces license and
  source policies.

## Disclosure Timeline

We target the following coordinated disclosure cadence:

1. **Day 0** – Report received.
2. **Day 0–3** – Acknowledge and assign a tracking identifier.
3. **Day 3–10** – Confirm, scope, and develop a fix.
4. **Day 10–30** – Notify downstream distributors under embargo.
5. **Day 30 (default)** – Public advisory + patched release.
6. **Earlier disclosure** – Possible by mutual agreement when
   exploitation is active in the wild.

Critical-severity issues may be disclosed earlier (≤7 days) when
active exploitation is confirmed.

## Recognition

We credit reporters in the published advisory unless they prefer to
remain anonymous. Hall-of-fame lists are maintained in
`SECURITY_HALL_OF_FAME.md` when one exists.

## Out of Scope

The following are generally **not** considered security vulnerabilities:

- Denial-of-service attacks requiring local code execution by the
  same user.
- Vulnerabilities in third-party dependencies that are not reachable
  from HeliosCLI's public API (report upstream instead).
- Compiler/toolchain bugs not introduced by HeliosCLI.
- Issues only exploitable after a user disables the sandbox
  (`--dangerously-bypass-approvals-and-sandbox` or equivalent) and
  past the explicit confirmation prompt.

## Contact

GitHub Security Advisories (preferred) or the address listed in
`CODEOWNERS` for the `SECURITY` group.
