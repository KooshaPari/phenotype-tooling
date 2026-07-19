# Harbor Phase 3 soak checklist log (soft)

**Suite home:** `phenotype-tooling/crates/benchora/harbor-soft`  
**Harbor fork/env:** [KooshaPari/portage-temp](https://github.com/KooshaPari/portage-temp)  
**sharecli no longer owns Harbor soft CI.**

Audit-v38 **C08 L76** — execution evidence for ADR 0005 Phase 3.
Plan: [`docs/harbor-phase3-soak.md`](../docs/harbor-phase3-soak.md).

**Clock:** starts on first `main` push after soak execution scaffold merges into the suite
home. Count only `harbor-eval-stub-soft.yml` runs where job
`Harbor eval stub (corpus preflight)` logs `STUB PASS: corpus valid`.

**Progress (2026-07-19 UTC):** `main` soak days complete **0 / 7** · remaining **7**.
Local soft parity is allowed for evidence but does **not** decrement the seven-day `main` clock.

**Backfill note (from sharecli extract):** Historical sharecli soak runs do **not** count
toward this suite clock. Leave **0/7** until phenotype-tooling suite workflows record
post-land consecutive green days.

## Seven consecutive `main` runs

| # | recorded_at_utc | git_sha | workflow_run | stub_pass | notes |
|---|-----------------|---------|--------------|-----------|-------|
| 1 | _pending_ | — | — | — | post-merge row 1 |
| 2 | _pending_ | — | — | — | |
| 3 | _pending_ | — | — | — | |
| 4 | _pending_ | — | — | — | |
| 5 | _pending_ | — | — | — | |
| 6 | _pending_ | — | — | — | |
| 7 | _pending_ | — | — | — | Phase 3 maintainer sign-off gate |

## Local soft parity (does not count toward 7/7)

| # | recorded_at_utc | git_sha | source | stub_pass | notes |
|---|-----------------|---------|--------|-----------|-------|
| L1 | 2026-07-19T01:47:13Z | 94ad489 | local | yes | sharecli-era `harbor_soak.sh` + `run-corpus.sh` (extracted; historical only) |

Append further local parity rows with:

```bash
export SHARECLI_ROOT=/path/to/sharecli
BENCHORA_HARBOR_SOAK_LOG=audit/harbor-phase3-soak-log.md \
  BENCHORA_HARBOR_SOAK_SOURCE=local \
  bash scripts/harbor_soak.sh
```

> Prefer editing this **Local soft parity** table manually after a run; the scaffold script
> appends a raw row at EOF and may not preserve table sections.

## Phase 3 checklist (manual)

- [ ] Seven consecutive `main` workflow runs green for `harbor-eval-stub-soft.yml`.
- [ ] No merged PRs broke sharecli `scripts/eval/run-corpus.sh` preflight on `main` during the window.
- [x] `harbor_soak.sh` reproduces CI locally on branch HEAD (scaffold + 2026-07-19 soft soak).
- [ ] Cross-repo pins table filled with recorded portage / pheno-harness refs.
- [ ] Maintainer acknowledges Phase 3 complete — **does not** mark ADR 0002 superseded (Phase 4).

## Cross-repo pins (recorded)

| Asset | Org repo | Recorded pin | Suite touchpoint |
|-------|----------|--------------|------------------|
| Harbor env provisioning | `KooshaPari/portage-temp` | _pending_ | `scripts/harbor_stub.sh` |
| SWE-bench / Terminal-Bench tasks | `phenotype-org/pheno-harness` | _pending_ | sharecli eval GOVERNANCE N/A rows |
| Adapter DAG | portage `adapters/pheno_harness_to_portage.py` | _pending_ | L71/L76 rubric cross-ref |

Canonical pin narrative for PORTAGE: `docs/ops/harbor-env-pins-from-sharecli.md`
in the portage worktree / portage-temp.

## Partial evidence (extracted scaffold)

| Evidence | Status |
|----------|--------|
| `scripts/harbor_soak.sh` local parity runner | Done (suite extract) |
| `workflows/harbor-soak-exec-soft.yml` CI soft job | Done (suite extract) |
| Checklist log template (this file) | Done |
| Local soft soak row L1 (2026-07-19, sharecli-era) | Historical only |
| Seven-day `main` soak window (suite home) | Open — **0/7 complete · 7 remaining** |
| L76 score bump | Deferred until soak completes + Phase 4 discussion |
