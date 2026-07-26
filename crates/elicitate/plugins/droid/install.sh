#!/usr/bin/env bash
# elicitate plugin install — Factory Droid (factory)
# Registers elicitate-mcp via direct write to ~/.factory/mcp.json
# and installs the elicitate skill into ~/.factory/skills/.

set -euo pipefail

SRC="/Users/kooshapari/CodeProjects/Phenotype/repos/phenotype-tooling"
BIN_DIR="$SRC/target/debug"

# 1. Resolve the elicitate-mcp binary
if ! command -v elicitate-mcp >/dev/null 2>&1; then
  TARGET="$BIN_DIR/elicitate-mcp"
  if [[ -x "$TARGET" ]]; then
    export PATH="$BIN_DIR:$PATH"
    echo "→ using elicitate-mcp from $TARGET"
  else
    echo "→ building elicitate-mcp..."
    (cd "$SRC" && cargo build -p elicitate --bin elicitate-mcp)
    export PATH="$BIN_DIR:$PATH"
  fi
fi

# 2. Write MCP server entry into ~/.factory/mcp.json
DROID_CONFIG="$HOME/.factory/mcp.json"
mkdir -p "$(dirname "$DROID_CONFIG")"
[[ -f "$DROID_CONFIG" ]] || echo '{}' > "$DROID_CONFIG"

python3 <<'PYEOF'
import json, os, pathlib

cfg_path = pathlib.Path(os.environ["DROID_CONFIG"])
text = cfg_path.read_text().strip()
cfg = json.loads(text) if text else {}

servers = cfg.setdefault("mcpServers", {})
servers["elicitate"] = {
    "command": "elicitate-mcp",
    "args": [],
    "transport": "stdio",
    "env": {
        "ELICITATE_INBOX_DIR": os.path.expanduser("~/.elicitate/inbox"),
    },
}

cfg_path.write_text(json.dumps(cfg, indent=2, sort_keys=False) + "\n")
print(f"✓ wrote {cfg_path}")
PYEOF
export DROID_CONFIG="$DROID_CONFIG"

# 3. Install the elicitate skill into ~/.factory/skills-dir/elicitate
SKILL_SRC="$SRC/crates/elicitate/.elicitate/skills/elicitate/SKILL.md"
SKILL_DIR="$HOME/.factory/skills-dir/elicitate"
SKILL_DEST="$SKILL_DIR/SKILL.md"
mkdir -p "$SKILL_DIR"
cp "$SKILL_SRC" "$SKILL_DEST"
echo "→ installed skill at $SKILL_DEST"

# 4. Verify
echo "→ verification:"
grep -q '"elicitate"' "$DROID_CONFIG" || { echo "FAIL: elicitate not registered in mcp.json"; exit 1; }
test -f "$SKILL_DEST" || { echo "FAIL: skill not installed"; exit 1; }
echo "✓ elicitate plugin installed for droid (factory)"
