#!/usr/bin/env bash
# Install elicitate plugin for Cursor.
#
# Usage:
#   ./install.sh [host-repo-path]
#
# If HOST_REPO is omitted, the current working directory is used.

set -euo pipefail

HOST_REPO="${1:-$PWD}"
ELICITATE_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "→ Installing elicitate plugin for Cursor into $HOST_REPO"

# 1. Merge cursor-mcp.json into .cursor/mcp.json (create if absent)
mkdir -p "$HOST_REPO/.cursor"
MCP_JSON="$HOST_REPO/.cursor/mcp.json"

if [ ! -f "$MCP_JSON" ]; then
    cp "$ELICITATE_DIR/plugins/cursor/cursor-mcp.json" "$MCP_JSON"
else
    # Merge using python (jq may not be installed everywhere)
    python3 - "$ELICITATE_DIR/plugins/cursor/cursor-mcp.json" "$MCP_JSON" <<'PYEOF'
import json, sys
new_path, existing_path = sys.argv[1], sys.argv[2]
with open(new_path) as f:
    new = json.load(f)
try:
    with open(existing_path) as f:
        existing = json.load(f)
except Exception:
    existing = {}
mcp = existing.setdefault("mcpServers", {})
for name, cfg in new.get("mcpServers", {}).items():
    if name not in mcp:
        mcp[name] = cfg
with open(existing_path, "w") as f:
    json.dump(existing, f, indent=2)
PYEOF
fi

# 2. Copy .cursorrules snippet; user appends manually to their .cursorrules
cp "$ELICITATE_DIR/plugins/cursor/.cursorrules" \
   "$HOST_REPO/.cursorrules.elicitate"

# 3. Verify elicitate-mcp is on PATH
if ! command -v elicitate-mcp >/dev/null 2>&1; then
    echo "warning: elicitate-mcp not found on PATH"
    echo "         install it with: cargo install --path $ELICITATE_DIR"
fi

echo "✓ elicitate installed for Cursor."
echo "  Append $HOST_REPO/.cursorrules.elicitate to your .cursorrules file."
echo "  Restart Cursor to activate the MCP server."