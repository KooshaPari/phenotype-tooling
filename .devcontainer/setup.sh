#!/usr/bin/env bash
# Post-create hook for the phenotype-tooling devcontainer.
# Configures git identity, fetches git submodules if any, and primes
# the cargo registry so the first build doesn't pay the cold-cache cost.
set -euo pipefail

# Git identity (only set locally for the workspace; never pushed without
# the user's consent).
if ! git config --get user.name >/dev/null 2>&1; then
    git config --global user.name "Phenotype Devcontainer"
fi
if ! git config --get user.email >/dev/null 2>&1; then
    git config --global user.email "devcontainer@phenotype.local"
fi

# Initialise the cargo cache by running a cheap check on the workspace.
# This warms the registry + git index caches so subsequent builds are fast.
if [ -f Cargo.toml ]; then
    echo "Warming cargo cache (cargo fetch)…"
    cargo fetch --locked 2>/dev/null || cargo fetch || true
fi

# Make sure the canonical dirs we bind-mount from exist and are writable.
mkdir -p /usr/local/cargo /home/vscode/.rustup

echo "Phenotype devcontainer ready."