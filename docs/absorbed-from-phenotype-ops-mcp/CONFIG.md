# Configuration

This repository reads runtime configuration from environment variables.
The variables below define the OmniRoute endpoint, logging behavior, tool exposure,
and execution safety limits for the MCP server process.

## Overview

All values are parsed at process startup.
Invalid values should fail fast during configuration loading.
Prefer explicit values in production rather than relying on shell defaults.
Keep secrets out of committed files and inject them through your process manager,
container runtime, or local shell profile.

## Environment Variables

### `OMNIROUTE_URL`

- Required: yes
- Type: string URL
- Default: none
- Purpose: Base URL for the OmniRoute service used by delegated operational calls.
- Validation:
  - Must be present.
  - Must be an absolute `http://` or `https://` URL.
  - Should not include a trailing path fragment unless the server expects one.
- Example values:
  - `http://127.0.0.1:20128`
  - `https://omniroute.internal.example.com`
- Security implications:
  - Treat this as sensitive infrastructure metadata.
  - Prefer `https` outside local development.
  - Avoid pointing at public endpoints without authentication or network controls.

### `LOG_LEVEL`

- Required: no
- Type: string enum
- Default: `info`
- Allowed values: `debug`, `info`, `warn`, `error`
- Purpose: Controls verbosity for server logs and diagnostic output.
- Validation:
  - Value should be normalized to lowercase before evaluation.
  - Any value outside the allowed set should be rejected.
- Example values:
  - `debug`
  - `info`
  - `error`
- Security implications:
  - `debug` may increase exposure of operational metadata in logs.
  - Use the lowest verbosity that still supports incident response.

### `TOOL_ALLOWLIST`

- Required: no
- Type: comma-separated string list
- Default: `health,dispatch,delegate`
- Purpose: Restricts the tool names exposed by the MCP server.
- Validation:
  - Empty entries should be trimmed out.
  - Values should be normalized for whitespace.
  - Unknown tool names should be rejected rather than silently ignored.
- Example values:
  - `health,dispatch,delegate`
  - `health`
  - `health,delegate`
- Security implications:
  - This is a primary surface-area control.
  - Keep the allowlist minimal in shared or production environments.
  - Review new tool additions before exposing them through this variable.

### `MAX_EXEC_TIMEOUT`

- Required: no
- Type: duration string
- Default: `30s`
- Purpose: Upper bound for a single delegated execution request.
- Validation:
  - Must parse as a Go duration such as `30s` or `1m`.
  - Must be greater than zero.
  - Should stay within operationally safe limits for your deployment tier.
- Example values:
  - `15s`
  - `30s`
  - `1m`
- Security implications:
  - Prevents resource exhaustion from long-running or stuck requests.
  - Avoid overly large values that widen denial-of-service risk.

### `MAX_PARALLEL`

- Required: no
- Type: integer
- Default: `4`
- Purpose: Maximum number of concurrent delegated operations.
- Validation:
  - Must be a whole number.
  - Must be greater than zero.
  - Should remain small enough to protect upstream services and local resources.
- Example values:
  - `1`
  - `4`
  - `8`
- Security implications:
  - Caps concurrency to reduce amplification during abusive or accidental bursts.
  - Higher values increase contention and blast radius during failures.

## Security

Do not commit real deployment values into source control.
Use `config.example.env` only as a template.
Prefer secret injection through CI/CD, launchd, systemd, Docker, or your shell.
Review logs when changing `LOG_LEVEL` to ensure sensitive context is not exposed.
Prefer private network routing or TLS for `OMNIROUTE_URL`.
Use the narrowest possible `TOOL_ALLOWLIST` in production.
Tune `MAX_EXEC_TIMEOUT` and `MAX_PARALLEL` conservatively to reduce abuse potential.
If a new environment variable is introduced, document its type, default, validation,
examples, and security impact here before shipping the change.
