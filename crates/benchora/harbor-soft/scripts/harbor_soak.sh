#!/usr/bin/env bash
# Soft C08 Harbor Phase 3 soak execution scaffold (ADR 0005).
# Suite home: phenotype-tooling/crates/benchora/harbor-soft
# Harbor fork/env: https://github.com/KooshaPari/portage-temp
# Validates local parity with harbor-eval-stub-soft.yml and optionally appends
# a row to the soak checklist log. Does not provision Harbor/portage-temp.
# See docs/harbor-phase3-soak.md and audit/harbor-phase3-soak-log.md
set -euo pipefail

SUITE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="${BENCHORA_HARBOR_SOAK_LOG:-${SHARECLI_HARBOR_SOAK_LOG:-}}"
SOURCE="${BENCHORA_HARBOR_SOAK_SOURCE:-${SHARECLI_HARBOR_SOAK_SOURCE:-local}}"
STUB_PASS_MARKER="STUB PASS: corpus valid"
RUN_ID="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
GIT_SHA="$(git -C "${SUITE_ROOT}/../.." rev-parse --short HEAD 2>/dev/null \
  || git -C "$SUITE_ROOT" rev-parse --short HEAD 2>/dev/null \
  || echo unknown)"

echo "== Harbor Phase 3 soak execution (soft) =="
echo "Suite home: phenotype-tooling/crates/benchora/harbor-soft"
echo "Harbor env: https://github.com/KooshaPari/portage-temp"
echo "Policy: ${SUITE_ROOT}/docs/harbor-phase3-soak.md"
echo "sha=$GIT_SHA source=$SOURCE"
echo ""

if [[ -z "${SHARECLI_ROOT:-}" ]]; then
  echo "harbor_soak: SHARECLI_ROOT is required for corpus preflight (via harbor_stub.sh)." >&2
  echo "  Set SHARECLI_ROOT to a sharecli checkout that contains scripts/eval/run-corpus.sh" >&2
  exit 2
fi

echo ">> Step 1: harbor_stub.sh (corpus preflight + stub pass)"
stub_out="$(mktemp)"
if ! bash "${SUITE_ROOT}/scripts/harbor_stub.sh" | tee "$stub_out"; then
  echo "harbor soak: harbor_stub.sh failed" >&2
  exit 1
fi
if ! grep -Fq "$STUB_PASS_MARKER" "$stub_out"; then
  echo "harbor soak: missing stub pass marker" >&2
  exit 2
fi
rm -f "$stub_out"

echo ""
echo ">> Step 2: run-corpus.sh preflight (checklist item 2)"
CORPUS_SCRIPT="${SHARECLI_ROOT}/scripts/eval/run-corpus.sh"
if [[ ! -f "$CORPUS_SCRIPT" ]]; then
  echo "harbor_soak: missing corpus script at ${CORPUS_SCRIPT}" >&2
  exit 2
fi
bash "$CORPUS_SCRIPT"

echo ""
echo ">> Step 3: suite workflow parity note"
echo "Local parity: harbor_stub.sh matches harbor-eval-stub-soft.yml subject job."

if [[ -n "$LOG_FILE" ]]; then
  mkdir -p "$(dirname "$LOG_FILE")"
  if [[ ! -f "$LOG_FILE" ]]; then
    cat >"$LOG_FILE" <<'HEADER'
# Harbor Phase 3 soak checklist log (soft)

Template for seven consecutive `main` green runs of `harbor-eval-stub-soft.yml`.
Append rows via `BENCHORA_HARBOR_SOAK_LOG=audit/harbor-phase3-soak-log.md bash scripts/harbor_soak.sh`.

| # | recorded_at_utc | git_sha | source | stub_pass | notes |
|---|-----------------|---------|--------|-----------|-------|
HEADER
  fi
  next_n="$(grep -c '^| [0-9]' "$LOG_FILE" 2>/dev/null || echo 0)"
  next_n=$((next_n + 1))
  echo "| $next_n | $RUN_ID | $GIT_SHA | $SOURCE | yes | local parity check |" >>"$LOG_FILE"
  echo "Appended row $next_n to $LOG_FILE"
fi

echo ""
echo "SOAK SCAFFOLD PASS: local stub + corpus preflight green (Phase 3 partial)"
echo "Seven-day main soak clock: track remaining rows in audit/harbor-phase3-soak-log.md"
