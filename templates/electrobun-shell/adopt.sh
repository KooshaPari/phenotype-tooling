#!/usr/bin/env bash
# phenotype-desktop adopt script
# Usage:
#   ./adopt.sh --app-name "MyApp" --app-id "com.example.myapp" \
#              --renderer-url "http://localhost:3000" \
#              --views-entrypoint "../web/dist/index.html" \
#              --compose "/path/to/process-compose.yml" \
#              --out /path/to/output/desktop
#
# Copies the template into --out, substitutes all __PLACEHOLDERS__, ready to `bun install && bun dev`.

set -euo pipefail

APP_NAME=""
APP_ID=""
APP_VERSION="0.1.0"
RENDERER_URL="http://localhost:3000"
VIEWS_ENTRYPOINT="../web/dist/index.html"
COMPOSE_FILE=""
OUT_DIR=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --app-name)        APP_NAME="$2";           shift 2 ;;
    --app-id)          APP_ID="$2";             shift 2 ;;
    --app-version)     APP_VERSION="$2";        shift 2 ;;
    --renderer-url)    RENDERER_URL="$2";       shift 2 ;;
    --views-entrypoint) VIEWS_ENTRYPOINT="$2";  shift 2 ;;
    --compose)         COMPOSE_FILE="$2";       shift 2 ;;
    --out)             OUT_DIR="$2";            shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

[[ -z "$APP_NAME" ]] && { echo "ERROR: --app-name required"; exit 1; }
[[ -z "$APP_ID"   ]] && { echo "ERROR: --app-id required";   exit 1; }
[[ -z "$OUT_DIR"  ]] && { echo "ERROR: --out required";       exit 1; }

TEMPLATE_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT_DIR/src"

# Copy & substitute
for SRC in electrobun.config.ts src/main.ts package.json tsconfig.json; do
  DEST="$OUT_DIR/$SRC"
  mkdir -p "$(dirname "$DEST")"
  sed \
    -e "s|__APP_NAME__|$APP_NAME|g" \
    -e "s|__APP_ID__|$APP_ID|g" \
    -e "s|__APP_VERSION__|$APP_VERSION|g" \
    -e "s|__DEFAULT_DEV_URL__|$RENDERER_URL|g" \
    -e "s|__VIEWS_ENTRYPOINT__|$VIEWS_ENTRYPOINT|g" \
    "$TEMPLATE_DIR/$SRC" > "$DEST"
done

# Write .env.example
cat > "$OUT_DIR/.env.example" <<EOF
# Override renderer URL (default: $RENDERER_URL)
RENDERER_URL=$RENDERER_URL

# Path to process-compose.yml for one-click service boot
# Leave unset to skip service boot
SERVICES_COMPOSE_FILE=${COMPOSE_FILE}

# Optional window size overrides
# WINDOW_WIDTH=1400
# WINDOW_HEIGHT=900
EOF

# Write Justfile tasks
cat > "$OUT_DIR/justfile" <<EOF
# ${APP_NAME} desktop shell
set dotenv-load

dev:
  bun dev

build:
  bun run build

release:
  bun run build:release

install:
  bun install

typecheck:
  bun run typecheck
EOF

echo ""
echo "Electrobun shell created at: $OUT_DIR"
echo ""
echo "Next steps:"
echo "  cd $OUT_DIR"
echo "  bun install          # macOS only — Electrobun requires macOS to build"
echo "  bun dev              # launches with RENDERER_URL=$RENDERER_URL"
echo ""
echo "Note: set SERVICES_COMPOSE_FILE in .env for one-click service boot."
