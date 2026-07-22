# Codex plugin — elicitate

Installs the `elicitate` MCP server + skill into Codex.

## Install

```bash
./install.sh                    # global: ~/.codex
./install.sh /path/to/host-repo # per-repo: <repo>/.codex
```

Or manually, copy `codex.toml` into your Codex MCP config and copy the
SKILL.md into your Codex skills directory.

## Verify

```bash
codex mcp list | grep elicitate_mcp
codex skills list | grep elicitate
```

## Uninstall

```bash
rm -rf ~/.codex/skills/elicitate
# Remove the [mcp_servers.elicitate_mcp] block from ~/.codex/mcp.toml
```