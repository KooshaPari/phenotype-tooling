#!/usr/bin/env bash
# Install elicitate plugin for Forge.
#
# Usage:
#   ./install.sh [host-repo-path]
#
# If HOST_REPO is omitted, the current working directory is used.

set -euo pipefail

HOST_REPO="${1:-$PWD}"
ELICITATE_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "→ Installing elicitate plugin for Forge into $HOST_REPO"

# 1. Copy the plugin manifest
mkdir -p "$HOST_REPO/.forgecode/plugins/elicitate"
cp "$ELICITATE_DIR/plugins/forgecode/plugin.toml" \
   "$HOST_REPO/.forgecode/plugins/elicitate/"

# 2. Symlink the skill
mkdir -p "$HOST_REPO/.forgecode/skills"
ln -sfn "$ELICITATE_DIR/.elicitate/skills/elicitate" \
        "$HOST_REPO/.forgecode/skills/elicitate"

# 3. Verify elicitate-mcp is on PATH
if ! command -v elicitate-mcp >/dev/null 2>&1; then
    echo "warning: elicitate-mcp not found on PATH"
    echo "         install it with: cargo install --path $ELICITATE_DIR"
    echo "         or:              brew install elicitate   (when available)"
fi

echo "✓ elicitate installed for Forge."
echo "  Restart Forgecode to activate."