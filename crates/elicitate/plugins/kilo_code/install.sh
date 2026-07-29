#!/usr/bin/env bash
# elicitate plugin install — Kilo Code (kilo)
# Registers elicitate-mcp via direct write to ~/.config/kilo/kilo.jsonc
# and installs the elicitate skill into ~/.kilo/skills/.

set -euo pipefail

SRC="/Users/kooshapari/CodeProjects/Phenotype/repos/phenotype-tooling"
BIN_DIR="$SRC/target/debug"

# 1. Resolve the elicitate-mcp binary (prefer installed, fall back to cargo target)
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

# 2. Write MCP server entry into ~/.config/kilo/kilo.jsonc
export KILO_CONFIG="$HOME/.config/kilo/kilo.jsonc"
mkdir -p "$(dirname "$KILO_CONFIG")"
[[ -f "$KILO_CONFIG" ]] || echo '{}' > "$KILO_CONFIG"

# Use Python to safely merge JSON (preserves comments in jsonc)
python3 <<'PYEOF'
import json, sys, re, os, pathlib

cfg_path = pathlib.Path(os.environ["KILO_CONFIG"])
text = cfg_path.read_text()

# Strip // and /* */ comments for JSON parsing (best-effort)
clean = re.sub(r"//.*", "", text)
clean = re.sub(r"/\*.*?\*/", "", clean, flags=re.DOTALL)
try:
    cfg = json.loads(clean) if clean.strip() else {}
except json.JSONDecodeError:
    cfg = {}

servers = cfg.setdefault("mcpServers", {})
servers["elicitate"] = {
    "command": "elicitate-mcp",
    "args": [],
    "transport": "stdio",
    "env": {
        "ELICITATE_INBOX_DIR": os.path.expanduser("~/.elicitate/inbox"),
    },
}

# Serialize back with trailing newline; preserve original ordering of other keys
new_text = json.dumps(cfg, indent=2, sort_keys=False)
cfg_path.write_text(new_text + "\n")
print(f"✓ wrote {cfg_path}")
PYEOF

# 3. Install the elicitate skill into ~/.kilo/skills/
SKILL_SRC="$SRC/crates/elicitate/.elicitate/skills/elicitate/SKILL.md"
SKILL_DEST="$HOME/.kilo/skills/elicitate/SKILL.md"
mkdir -p "$(dirname "$SKILL_DEST")"
cp "$SKILL_SRC" "$SKILL_DEST"
echo "→ installed skill at $SKILL_DEST"

# 4. Verify
echo "→ verification:"
grep -q '"elicitate"' "$KILO_CONFIG" || { echo "FAIL: elicitate not registered in kilo.jsonc"; exit 1; }
test -f "$SKILL_DEST" || { echo "FAIL: skill not installed"; exit 1; }
echo "✓ elicitate plugin installed for kilo (kilo_code)"