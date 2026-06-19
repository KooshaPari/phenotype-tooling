---
title: "Threat Model"
version: 0.1.0
lastUpdated: 2026-06-16
---

# Threat Model

> **Source of truth:** helios-router (Streamlit dashboard for Pareto analysis of LLM provider/model selection and ledger management)
> **Scope:** Streamlit web app, LLM provider integration, ledger DB, dashboard widgets, deployment

## Assets

1. **Streamlit web app** — Python web app served via `streamlit run`. If mutable, an attacker can ship a script that runs arbitrary code at server start.
2. **LLM provider API keys** — `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OMNIROUTE_AUTH_TOKEN` read from env. Compromise allows an adversary to rack up cost or feed prompts that game the dashboard.
3. **Ledger DB** — Records Pareto choices, cost, latency. If mutable, an adversary can rewrite history to favor a malicious provider.
4. **Dashboard widgets** — Plotly charts, tables, filters. If mutable, can inject HTML/JS that exfiltrates session cookies.
5. **Provider selection logic** — The Pareto algorithm itself. If mutable, an attacker can bias the selection toward a malicious provider.

## Threats (STRIDE)

| Category | Threat | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **Spoofing** | An adversary publishes a `helios-router` fork under a similar PyPI name and downstream CI tools fetch the wrong package. | Low | Critical | The package is published under the canonical PyPI name. README documents the canonical install path. Pip is configured to use `--require-hashes` in CI. |
| **Tampering** | A Pareto selection rule is modified to silently favor a malicious provider. | Low | High | The rule set is versioned and signed. The selection logic is in a separate module with unit tests; tests fail on rule changes without version bump. |
| **Repudiation** | A contributor pushes a rule change and later denies it. | Low | Medium | All commits are signed (gitsign, keyless). Releases are tagged. The git history is the audit trail. |
| **Information Disclosure** | The Streamlit app's `secrets.toml` is committed by accident. | High | High | `.streamlit/secrets.toml` is in `.gitignore`. CI runs `gitleaks` on every PR. Streamlit is configured to read secrets from env, not from `secrets.toml`, when deployed. |
| **Denial of Service** | A malicious or oversized LLM request (a 1M-token prompt) causes the dashboard to OOM. | Medium | Medium | Streamlit enforces `max-request-bytes=1MB` and a `request-timeout=60s`. Inputs over the limit return a clear error. |
| **Elevation of Privilege** | A malicious Python dependency in the workspace executes arbitrary code at install time. | Low | Critical | `poetry.lock` is committed; CI uses `poetry install --no-dev` for production. `pip-audit` and `safety check` run on every PR. The dashboard runs in a container with read-only FS and no network egress by default. |

## Residual Risk and Revision Cadence

The most material residual risk is **Streamlit app compromise** — if a malicious change ships, every dashboard user is affected at once. The strongest available mitigation is the gitleaks pre-commit hook + commit signing, but these do not catch a deliberately obfuscated payload. The next highest residual is **ledger DB tampering** — a malicious actor with DB write access can rewrite history. This threat model should be revised quarterly (February, May, August, November) or whenever a new LLM provider is added, a new widget is integrated, or the deployment target changes. The revision trigger is any PR that adds a new provider, a new widget, or a new public-facing endpoint.
