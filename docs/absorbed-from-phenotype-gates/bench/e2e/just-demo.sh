#!/usr/bin/env bash
# Reproduces the e2e flow on a fresh fixture scratch.
# This is what `just demo` invokes.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
scratch="$root/bench/fixture.demo"
rm -rf "$scratch"
cp -R "$root/bench/fixture" "$scratch"
rm -f "$scratch/gates.lock.json"
node "$root/src/cli.js" check "$scratch" || true
node "$root/src/cli.js" fix --gate FR-PGAT-008 "$scratch"
node "$root/src/cli.js" check "$scratch"
echo "just demo: ok"
