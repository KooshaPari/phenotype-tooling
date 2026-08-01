#!/usr/bin/env bash
# Install elicitate plugin for Codex.
#
# Usage:
#   ./install.sh [host-repo-path]
#
# If HOST_REPO is omitted, ~/.codex is used for global install.

set -euo pipefail

HOST_REPO="${1:-$HOME/.codex}"
ELICITATE_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "→ Installing elicitate plugin for Codex into $HOST_REPO"

# 1. Copy the skill
mkdir -p "$HOST_REPO/skills/elicitate"
cp -r "$ELICITATE_DIR/.elicitate/skills/elicitate/." \
      "$HOST_REPO/skills/elicitate/"

# 2. Merge the MCP server entry into mcp.toml (create if absent)
MCP_TOML="$HOST_REPO/mcp.toml"
if [ ! -f "$MCP_TOML" ]; then
    cat > "$MCP_TOML" <<'EOF'
# Codex MCP servers — managed.

EOF
fi

if ! grep -q 'elicitate_mcp' "$MCP_TOML"; then
    cat >> "$MCP_TOML" <<'EOF'

# elicitate (added by plugins/elicitate/install.sh)
[mcp_servers.elicitate_mcp]
command = "elicitate-mcp"
disabled = false
trust_level = "trusted"
EOF
fi

# 3. Verify elicitate-mcp is on PATH
if ! command -v elicitate-mcp >/dev/null 2>&1; then
    echo "warning: elicitate-mcp not found on PATH"
    echo "         install it with: cargo install --path $ELICITATE_DIR"
fi

echo "✓ elicitate installed for Codex."
echo "  Restart Codex to activate."
