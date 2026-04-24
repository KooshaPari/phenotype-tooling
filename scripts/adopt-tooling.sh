#!/bin/bash
# Symlink phenotype-tooling binaries into target repo's tooling/ dir.
# Bash-only because it's a ≤5-line shell glue wrapper per scripting policy.

TOOLING_ROOT="$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")"
TARGET_DIR="${1:-.}/tooling"

mkdir -p "$TARGET_DIR"
for bin in agent-orchestrator audit-privacy bench-guard commit-msg-check doc-link-check fr-coverage release-cut sbom-gen fuzz-setup; do
  ln -sf "$TOOLING_ROOT/target/release/$bin" "$TARGET_DIR/$bin"
done
echo "✓ Adopted phenotype-tooling binaries (9 tools) → $TARGET_DIR"
