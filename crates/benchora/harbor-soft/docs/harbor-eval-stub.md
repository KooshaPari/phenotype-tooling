# Harbor eval stub (soft) — benchora suite

**Suite home:** `phenotype-tooling/crates/benchora/harbor-soft`  
**Harbor fork/env:** [KooshaPari/portage-temp](https://github.com/KooshaPari/portage-temp)  
**sharecli no longer owns Harbor soft CI.**

Audit-v38 **C08 L71 / L76**. Phase 2 stub for the agent-eval supersede pathway
(ADR 0005 in sharecli). Harbor / portage-temp / Terminal-Bench task runs remain
**N/A** until Phase 4 supersede. This tree is **suite-facing only**.

## Soft contract (Phase 2)

| Step | Action | Hard gate? |
|------|--------|------------|
| 1 | Validate supervisor JSON via sharecli `run-corpus.sh` (`SHARECLI_ROOT` required) | No |
| 2 | Print **STUB PASS** — no Harbor env provisioned in this crate | No |
| 3 | Soft CI: `workflows/harbor-eval-stub-soft.yml` with `continue-on-error: true` | No |

Corpus preflight is **sharecli-local**. Set `SHARECLI_ROOT` to a sharecli checkout
that contains `scripts/eval/run-corpus.sh`. If unset, `harbor_stub.sh` exits **2**
with a clear error (no silent degrade). Do **not** use relative
`../../../sharecli` paths.

## Local run

```bash
export SHARECLI_ROOT=/path/to/sharecli
bash scripts/harbor_stub.sh
```

Expected tail output:

```
STUB PASS: corpus valid; Harbor task runner not wired (Phase 2 soft)
Harbor/portage-temp env provisioning deferred — see docs/harbor-phase3-soak.md
```

## CI workflow

Workflow: [`workflows/harbor-eval-stub-soft.yml`](../workflows/harbor-eval-stub-soft.yml)
(suite-layer reference; wire from phenotype-tooling, not sharecli).

| Trigger | Paths |
|---------|-------|
| `pull_request` | any |
| `push` to `main` | `crates/benchora/harbor-soft/**` |

## Phase map (ADR 0005)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 0 | Supervisor corpus + ADR 0002 (sharecli) | Done |
| 1 | ADR 0005 supersede plan (sharecli) | Done |
| **2** | **This doc + `harbor_stub.sh` (benchora suite)** | **Done (soft)** |
| 3 | [`harbor-phase3-soak.md`](./harbor-phase3-soak.md) + seven-day soft soak | In progress (scaffold landed) |
| 4 | Mark ADR 0002 superseded; GOVERNANCE + lane re-score | Deferred |

Phase 3 soak evidence plan: [`harbor-phase3-soak.md`](./harbor-phase3-soak.md).
Cross-repo Harbor env pins: portage `docs/ops/harbor-env-pins*.md` /
[portage-temp](https://github.com/KooshaPari/portage-temp).

**Status:** soft stub (Phase 2) · **FR:** FR-003 traceability · **Last sync:** 2026-07-19
