#!/usr/bin/env bash
# check-gitignore-template.sh
#
# Flags repos whose .gitignore is a trivial cluster pattern (≤5 lines,
# single stack) without referencing one of the canonical templates at
# https://github.com/KooshaPari/phenotype-tooling/tree/main/templates
#
# Exit code 0 = OK (adopted or non-trivial)
# Exit code 1 = WARN (trivial pattern, not adopted)
# Exit code 2 = ERROR (no .gitignore at all)
set -euo pipefail

if [ ! -f .gitignore ]; then
  echo "::error::No .gitignore file"
  exit 2
fi

# Count non-blank, non-comment lines
body_lines=$(grep -vE '^\s*(#|$)' .gitignore | wc -l | tr -d ' ')

# Detect stack by marker files
stacks=()
[ -f Cargo.toml ]    && stacks+=("rust")
[ -f pyproject.toml ] || [ -f setup.py ] && stacks+=("python")
[ -f package.json ]  && stacks+=("node")
ls *.xcodeproj 2>/dev/null | head -1 > /dev/null && stacks+=("ios")

# If Source comment is present, treat as adopted
if grep -qE '^# Source:.*phenotype-tooling.*gitignore' .gitignore; then
  echo "Adopted (Source comment present, body_lines=$body_lines)"
  exit 0
fi

# If body is trivial (≤5 lines), flag it
if [ "$body_lines" -le 5 ]; then
  echo "::warning::Trivial .gitignore ($body_lines lines) without template reference. See https://github.com/KooshaPari/phenotype-tooling/blob/main/docs/gitignore-adoption.md"
  exit 1
fi

# Otherwise, OK (non-trivial, repo-specific .gitignore)
echo "Non-trivial .gitignore (body_lines=$body_lines, stacks=${stacks[*]:-none})"
exit 0
