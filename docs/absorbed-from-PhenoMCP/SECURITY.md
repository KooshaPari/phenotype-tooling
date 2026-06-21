# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in **PhenoMCP**, please report it privately via GitHub's security advisories:

- https://github.com/KooshaPari/PhenoMCP/security/advisories/new

Please do **not** open a public issue for security reports. We will acknowledge receipt within 72 hours and provide a remediation timeline based on severity.

## Scope

This policy covers the latest released version on the `main` branch. Older releases are not actively maintained.

## Threat model

A STRIDE-per-component threat model is maintained at [`docs/security/threat-model.md`](docs/security/threat-model.md).
It covers the MCP protocol handler, FastMCP transport bridge, tool registry, backend adapter crates
(Meilisearch, Qdrant, SurrealDB), the polyglot supply chain, and the CI/CD pipeline.
Review the threat model before opening a public advisory for design-level issues.

## Disclosure

We follow a coordinated disclosure model. Once a fix is available and deployed, we will publish a public advisory crediting the reporter (unless anonymity is requested).
