#!/usr/bin/env bash
# check-codeowners-template.sh
#
# Flags repos whose .github/CODEOWNERS is exactly "* @KooshaPari"
# without referencing the canonical template at
# https://github.com/KooshaPari/phenotype-tooling/blob/main/templates/CODEOWNERS
#
# Exit code 0 = OK (adopted or has a non-trivial CODEOWNERS)
# Exit code 1 = WARN (trivially `* @KooshaPari`, not adopted)
# Exit code 2 = ERROR (no .github/CODEOWNERS file at all)
set -euo pipefail

if [ ! -f .github/CODEOWNERS ]; then
  echo "::error::No .github/CODEOWNERS file"
  exit 2
fi

# Strip blank lines and comments
body=$(grep -vE '^\s*(#|$)' .github/CODEOWNERS | tr -d '[:space:]')

if [ "$body" = "*@KooshaPari" ]; then
  # Check for the Source: comment
  if grep -qE '^# Source:.*phenotype-tooling' .github/CODEOWNERS; then
    echo "Adopted (trivial pattern + Source comment)"
    exit 0
  else
    echo "::warning::Trivial CODEOWNERS (\`* @KooshaPari\`) without template reference. See https://github.com/KooshaPari/phenotype-tooling/blob/main/docs/codeowners-adoption.md"
    exit 1
  fi
else
  echo "Non-trivial CODEOWNERS (OK)"
  exit 0
fi
