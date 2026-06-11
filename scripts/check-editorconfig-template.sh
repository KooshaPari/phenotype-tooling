#!/usr/bin/env bash
# check-editorconfig-template.sh
#
# Flags repos whose .editorconfig is the canonical pattern without
# a template-reference comment.
#
# Exit code 0 = OK (adopted or non-canonical)
# Exit code 1 = WARN (canonical pattern, not adopted)
# Exit code 2 = ERROR (no .editorconfig at all)
set -euo pipefail

if [ ! -f .editorconfig ]; then
  echo "::error::No .editorconfig file"
  exit 2
fi

# If Source comment is present, treat as adopted (matches the template's Source: comment)
if grep -qF 'phenotype-tooling' .editorconfig && grep -qE '^# Source:.*editorconfig' .editorconfig; then
  echo "Adopted (Source comment present)"
  exit 0
fi

# Canonical pattern detection: check for the key markers (fixed strings, robust)
if grep -qFx 'root = true' .editorconfig \
   && grep -qFx '[*]' .editorconfig \
   && grep -qFx '[*.{rs,go}]' .editorconfig; then
  echo "::warning::Canonical .editorconfig pattern without template reference. See https://github.com/KooshaPari/phenotype-tooling/blob/main/docs/editorconfig-adoption.md"
  exit 1
fi

# Otherwise, OK (non-canonical, repo-specific .editorconfig)
echo "Non-canonical .editorconfig (OK, repo-specific)"
exit 0
