---
title: "Threat Model"
version: 0.1.0
lastUpdated: 2026-06-16
---

# Threat Model

> **Source of truth:** phenotype-zod-schemas (Phenotype Zod schema bundle — shared TypeScript runtime validators for fleet frontends)
> **Scope:** Zod schema definitions, runtime validation, schema versioning, build pipeline, distribution

## Assets

1. **Zod schema definitions (`src/schemas/*.ts`)** — Exported TypeScript types derived from `z.object(...)` calls. Consumers depend on these for runtime input validation. A schema change is a breaking change.
2. **Generated TypeScript types (`dist/*.d.ts`)** — Inferred from Zod schemas via `z.infer<>`. If mutable, consumers receive incorrect types at build time.
3. **Distribution bundle (`dist/index.js`, `dist/index.mjs`)** — Published to npm. If mutable in transit, consumers fetch a backdoored bundle.
4. **CI pipeline (GitHub Actions)** — Runs `tsc`, builds, and publishes. If mutable, can inject backdoors.
5. **Schema version metadata (`package.json#version`)** — Semver. Downgrade attacks rely on consumers installing a lower-versioned package.

## Threats (STRIDE)

| Category | Threat | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **Spoofing** | An adversary publishes a `phenotype-zod-schemas` package under a similar name (e.g., `phenotype-zod` or `@kooshapari/zod-schemas` with a private scope) and downstream `npm install` resolves the wrong package. | Low | Critical | All release artifacts are published under the canonical npm name `phenotype-zod-schemas`. The README documents the canonical install command. The package is signed with npm provenance (Sigstore). |
| **Tampering** | A schema is modified in a release to silently accept invalid input (false negative validation). | Low | High | The `package-lock.json` is committed and CI runs `npm ci` on every build. Schemas are versioned with semver; consumers can pin to a specific version. |
| **Repudiation** | A contributor pushes a schema change and later denies it. | Low | Medium | All commits are signed (gitsign, keyless). Releases are tagged. The git history is the audit trail. |
| **Information Disclosure** | A schema definition accidentally includes a sensitive field (e.g., a `password` field) that gets logged when validation fails. | Medium | Medium | CI runs a `secret-pattern-scan` step on every PR. Schemas are reviewed for sensitive fields before merge. The Zod `.refine()` API is documented to redact, not log. |
| **Denial of Service** | A malicious or malformed input to a Zod `.refine()` callback causes a DoS in a downstream consumer (e.g., a regex with catastrophic backtracking). | Medium | Medium | All `.refine()` callbacks are tested with adversarial inputs. CI runs `zod-test` (fuzz tests) on every push. The `safeParse` API is preferred over `parse` to avoid throwing on invalid input. |
| **Elevation of Privilege** | A malicious npm package in the dependency tree executes arbitrary code at install time (via `postinstall` script). | Low | Critical | `npm ci --ignore-scripts` is the default in CI. Dependencies are pinned via the lockfile. `npm audit` runs on every PR. npm provenance is verified on every install. |

## Residual Risk and Revision Cadence

The most material residual risk is **typosquatted npm package** — if a downstream consumer mistypes the package name, npm may resolve to a different package. The strongest available mitigation is the canonical name documentation in the README + npm provenance signing, but npm has no built-in typo defense. The next highest residual is **downgrade attacks** — a consumer who has pinned to `^1.0.0` may fetch a malicious 0.x version if a major-version mistake allows it. This threat model should be revised quarterly (February, May, August, November) or whenever a new schema is added, a major version is bumped, or a new validation rule is introduced. The revision trigger is any PR that adds a new schema, modifies a `z.refine()` callback, or changes the export pattern.
