#!/usr/bin/env bash
# Smoke-build Go submodule planes under third_party/.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export GOPROXY="${GOPROXY:-https://proxy.golang.org,direct}"

failed=()

# Bifrost transports/go.mod pins published modules; monorepo builds need local replaces
# (same pattern as third_party/bifrost/nix/packages/bifrost-http.nix).
ensure_bifrost_transports_replaces() {
  local gomod="$1/go.mod"
  [[ -f "$gomod" ]] || return 0
  if grep -q '^replace github.com/maximhq/bifrost/core =>' "$gomod"; then
    return 0
  fi
  cat >>"$gomod" <<'EOF'

replace github.com/maximhq/bifrost/core => ../core
replace github.com/maximhq/bifrost/framework => ../framework
replace github.com/maximhq/bifrost/plugins/governance => ../plugins/governance
replace github.com/maximhq/bifrost/plugins/compat => ../plugins/compat
replace github.com/maximhq/bifrost/plugins/logging => ../plugins/logging
replace github.com/maximhq/bifrost/plugins/maxim => ../plugins/maxim
replace github.com/maximhq/bifrost/plugins/otel => ../plugins/otel
replace github.com/maximhq/bifrost/plugins/semanticcache => ../plugins/semanticcache
replace github.com/maximhq/bifrost/plugins/telemetry => ../plugins/telemetry
EOF
}

smoke() {
  local name="$1" rel="$2" sub="${3:-.}"
  local dir="$ROOT/$rel/$sub"
  if [[ ! -f "$dir/go.mod" ]]; then
    echo "SKIP $name: no go.mod in $sub"
    return 0
  fi
  if [[ "$name" == "bifrost-transports" ]]; then
    ensure_bifrost_transports_replaces "$dir"
  fi
  echo "==> smoke $name ($dir)"
  if ! (cd "$dir" && go build ./...); then
    failed+=("$name")
  fi
}

smoke agentapi-plusplus third_party/agentapi-plusplus .
smoke cliproxyapi-plusplus third_party/cliproxyapi-plusplus .
smoke cliproxy-package packages/cliproxy .
smoke agentapi-package packages/agentapi .
smoke bifrost-package packages/bifrost .
smoke argis-package packages/argis .
smoke argis-extensions third_party/argis-extensions .
smoke bifrost-transports third_party/bifrost transports

if ((${#failed[@]})); then
  echo "SMOKE FAIL: ${failed[*]}"
  exit 1
fi
echo "SMOKE OK"
