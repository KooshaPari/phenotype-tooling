#!/usr/bin/env bash
# Soft C08 Harbor eval stub (ADR 0005 Phase 2).
# Suite home: phenotype-tooling/crates/benchora/harbor-soft
# Harbor fork/env: https://github.com/KooshaPari/portage-temp
# Corpus preflight is sharecli-local (requires SHARECLI_ROOT); stub itself is suite-layer only.
set -euo pipefail

SUITE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "== Harbor eval stub (ADR 0005 Phase 2) =="
echo "Suite home: phenotype-tooling/crates/benchora/harbor-soft"
echo "Harbor env: https://github.com/KooshaPari/portage-temp"
echo "Ops:   ${SUITE_ROOT}/docs/harbor-eval-stub.md"
echo ""

if [[ -z "${SHARECLI_ROOT:-}" ]]; then
  echo "harbor_stub: SHARECLI_ROOT is required for supervisor corpus preflight." >&2
  echo "  Set SHARECLI_ROOT to a sharecli checkout that contains scripts/eval/run-corpus.sh" >&2
  echo "  Example: export SHARECLI_ROOT=/path/to/sharecli" >&2
  echo "  Corpus preflight is sharecli-local; this stub is suite-layer only." >&2
  exit 2
fi

CORPUS_SCRIPT="${SHARECLI_ROOT}/scripts/eval/run-corpus.sh"
if [[ ! -f "$CORPUS_SCRIPT" ]]; then
  echo "harbor_stub: missing corpus script at ${CORPUS_SCRIPT}" >&2
  echo "  SHARECLI_ROOT=${SHARECLI_ROOT}" >&2
  exit 2
fi

echo ">> Preflight: supervisor corpus fixtures (SHARECLI_ROOT=${SHARECLI_ROOT})"
bash "$CORPUS_SCRIPT"

echo ""
echo "STUB PASS: corpus valid; Harbor task runner not wired (Phase 2 soft)"
echo "Harbor/portage-temp env provisioning deferred — see docs/harbor-phase3-soak.md"
