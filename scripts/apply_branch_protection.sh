#!/usr/bin/env bash
# WP-14: apply branch protection to `main`.
#
# Prerequisites:
#   - gh CLI authenticated with admin:repo scope
#   - Working directory: repo root
#
# Usage:
#   bash scripts/apply_branch_protection.sh
#
# The script is idempotent. Re-running with the same JSON file produces
# the same end state. To tighten rules (e.g. add a new required check),
# edit .github/branch-protection/main.json first, then re-run.

set -euo pipefail

REPO="${REPO:-KooshaPari/phenotype-tooling}"
BRANCH="${BRANCH:-main}"
PAYLOAD_FILE="${PAYLOAD_FILE:-.github/branch-protection/main.json}"

if ! command -v gh >/dev/null 2>&1; then
  echo "error: gh CLI not found in PATH" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "error: gh CLI not authenticated (run: gh auth login)" >&2
  exit 1
fi

if [[ ! -f "${PAYLOAD_FILE}" ]]; then
  echo "error: ${PAYLOAD_FILE} not found" >&2
  exit 1
fi

echo "==> Applying branch protection to ${REPO}:${BRANCH}"
echo "    payload: ${PAYLOAD_FILE}"

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+3" \
  "repos/${REPO}/branches/${BRANCH}/protection" \
  --input "${PAYLOAD_FILE}"

echo
echo "==> Current protection state:"
gh api "repos/${REPO}/branches/${BRANCH}/protection" \
  | jq '{
      required_signatures: .required_signatures.enabled,
      required_linear_history: .required_linear_history.enabled,
      required_status_checks: .required_status_checks.contexts,
      enforce_admins: .enforce_admins.enabled,
      required_approving_review_count: .required_pull_request_reviews.required_approving_review_count,
      require_code_owner_reviews: .required_pull_request_reviews.require_code_owner_reviews,
      block_force_pushes: .allow_force_pushes.enabled | not,
      block_deletions: .allow_deletions.enabled | not,
      required_conversation_resolution: .required_conversation_resolution.enabled
    }'
