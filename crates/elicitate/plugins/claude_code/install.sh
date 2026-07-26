#!/usr/bin/env bash
# Install elicitate plugin for Claude Code v2.x
#
# Discovery paths used by Claude Code 2.1.197:
#   - MCP server catalog : ~/.claude.json    (mcpServers object)
#   - Skills             : ~/.claude/skills/<name>/SKILL.md
#   - Commands           : ~/.claude/commands/<name>.md
#   - Plugins            : ~/.claude/plugins/<name>/plugin.json
#
# We write directly to these JSON files because the `claude` CLI on this
# v2.1.x build does not expose a `claude mcp add` or `claude plugin install`
# subcommand (only the desktop app does). The CLI is a thin wrapper; the
# config is the source of truth and is read by the desktop app + the
# daemonised assistant.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRATE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SKILL_SRC="$CRATE_ROOT/.elicitate/skills/elicitate/SKILL.md"
BIN_DIR="$CRATE_ROOT/target/release"
ELICITATE_BIN_DIR="${ELICITATE_BIN_DIR:-$BIN_DIR}"

# 1) Resolve the elicitate-mcp binary path
if command -v elicitate-mcp >/dev/null 2>&1; then
    ELICITATE_MCP_BIN="$(command -v elicitate-mcp)"
elif [ -x "$ELICITATE_BIN_DIR/elicitate-mcp" ]; then
    ELICITATE_MCP_BIN="$ELICITATE_BIN_DIR/elicitate-mcp"
elif [ -x "$ELICITATE_BIN_DIR/elicitate" ]; then
    ELICITATE_MCP_BIN="$ELICITATE_BIN_DIR/elicitate"
else
    echo "[claude_code] elicitate-mcp not on PATH; install elicitate first (cargo install --path $CRATE_ROOT --bin elicitate-mcp)." >&2
    exit 1
fi

CLAUDE_JSON="$HOME/.claude.json"

# 2) Register MCP server in ~/.claude.json
echo "[claude_code] Writing elicitate-mcp to $CLAUDE_JSON..."
if [ -f "$CLAUDE_JSON" ]; then
    # Use python3 for safe JSON manipulation (jq may not be available on all systems)
    python3 - "$CLAUDE_JSON" "$ELICITATE_MCP_BIN" <<'PYEOF'
import json
import sys
path, cmd = sys.argv[1], sys.argv[2]
with open(path, "r") as f:
    cfg = json.load(f)
cfg.setdefault("mcpServers", {})
cfg["mcpServers"]["elicitate-mcp"] = {
    "type": "stdio",
    "command": cmd,
    "args": [],
    "env": {},
}
with open(path, "w") as f:
    json.dump(cfg, f, indent=2)
print(f"  registered mcpServers.elicitate-mcp -> {cmd}")
PYEOF
else
    cat > "$CLAUDE_JSON" <<EOF
{
  "mcpServers": {
    "elicitate-mcp": {
      "type": "stdio",
      "command": "$ELICITATE_MCP_BIN",
      "args": [],
      "env": {}
    }
  }
}
EOF
    echo "  created $CLAUDE_JSON with elicitate-mcp entry"
fi

# 3) Install skill
if [ ! -f "$SKILL_SRC" ]; then
    echo "[claude_code] SKILL.md not found at $SKILL_SRC" >&2
    exit 1
fi
mkdir -p "$HOME/.claude/skills/elicitate"
ln -sf "$SKILL_SRC" "$HOME/.claude/skills/elicitate/SKILL.md"
echo "  symlinked $HOME/.claude/skills/elicitate/SKILL.md"

# 4) Install plugin manifest (Claude Code 2.x reads these directly)
mkdir -p "$HOME/.claude/plugins/elicitate"
cat > "$HOME/.claude/plugins/elicitate/plugin.json" <<EOF
{
  "name": "elicitate",
  "version": "$(elicitate --version 2>/dev/null | awk '{print $2}' || echo '0.9.0')",
  "description": "elicitate MCP server + skill for Claude Code",
  "mcpServers": {
    "elicitate-mcp": {
      "type": "stdio",
      "command": "$ELICITATE_MCP_BIN",
      "args": [],
      "env": {}
    }
  },
  "skills": [
    {
      "name": "elicitate",
      "path": "$HOME/.claude/skills/elicitate/SKILL.md"
    }
  ]
}
EOF
echo "  wrote $HOME/.claude/plugins/elicitate/plugin.json"

# 5) Smoke
echo "[claude_code] Smoke: elicitate --version"
elicitate --version

echo "[claude_code] OK."
