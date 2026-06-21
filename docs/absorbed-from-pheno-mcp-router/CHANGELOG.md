# Changelog — pheno-mcp-router

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.1.0] - 2026-06-11

### Added

- Initial scaffold from V11 prep agent design (V4 §78.6, the substrate for all pheno-mcp servers).
- `McpRouter` dataclass: name, backend_url, sanitize_keys, response_keys, max_message_bytes, max_response_bytes, timeout_seconds
- `add_tier(name, route)` / `add_tool(tier, fn)` fluent API
- `_sanitize_payload` / `_allowlist_response` private helpers (the security contract)
- `pheno-mcp-router init <name>` CLI scaffolds a new MCP server using McpRouter
- 3 smoke tests (add_tier, add_tool error path, response allowlist)
- pyproject.toml, justfile, ci.yml, AGENTS.md, llms.txt, .gitignore
[Unreleased]: https://github.com/KooshaPari/pheno-mcp-router/compare/HEAD
