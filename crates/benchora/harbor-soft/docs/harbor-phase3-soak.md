# Harbor Phase 3 soak evidence plan (soft) — benchora suite

**Suite home:** `phenotype-tooling/crates/benchora/harbor-soft`  
**Harbor fork/env:** [KooshaPari/portage-temp](https://github.com/KooshaPari/portage-temp)  
**sharecli no longer owns Harbor soft CI.**

Audit-v38 **C08 L76 / L80**. Phase 3 soak contract for the agent-eval supersede pathway
(ADR 0005). Builds on the Phase 2 stub ([`harbor-eval-stub.md`](./harbor-eval-stub.md)).
Harbor / portage-temp / Terminal-Bench task runs remain **N/A** until Phase 4 supersede.

## Soft contract (Phase 3)

| Step | Action | Hard gate? |
|------|--------|------------|
| 1 | Document cross-repo Harbor env pins (portage + pheno-harness) | No |
| 2 | Track seven consecutive `main` green runs of `harbor-eval-stub-soft.yml` | No |
| 3 | Record soak evidence in PR comments or `audit/` | No |
| 4 | CI stays `continue-on-error: true` — no branch protection | No |

Phase 3 does **not** provision Harbor in this crate. The stub (`harbor_stub.sh`) continues
to validate supervisor corpus fixtures (via `SHARECLI_ROOT`) and print **STUB PASS**.
Soak proves the soft harness is stable on `main` before any Phase 4 supersede discussion.

## Cross-repo env pins (documented, not vendored)

Per ADR 0005 §Consequences, portage and pheno-harness stay **out of this suite crate**
until Phase 4. Canonical pin table for Harbor env lives in portage
(`docs/ops/harbor-env-pins*.md`) / [portage-temp](https://github.com/KooshaPari/portage-temp).
Track pins here for auditors and future wiring:

| Asset | Org repo | Pin / ref | Suite touchpoint |
|-------|----------|-----------|------------------|
| Harbor env provisioning | `KooshaPari/portage-temp` (was `phenotype-org/portage`) | `main` @ next tag after soak | `scripts/harbor_stub.sh` tail defers here |
| SWE-bench / Terminal-Bench tasks | `phenotype-org/pheno-harness` | task corpus via `pheno_harness_to_portage.py` | eval GOVERNANCE N/A rows (sharecli) |
| Adapter DAG | portage `adapters/pheno_harness_to_portage.py` | cross-repo only | L71/L76 rubric cross-ref |

Update the **Recorded pin** column in soak PRs when org repos cut a release relevant to
the supersede trigger (§Decision.2 in ADR 0005).

## CI workflow (soak subject)

Workflow: [`workflows/harbor-eval-stub-soft.yml`](../workflows/harbor-eval-stub-soft.yml)

| Trigger | Paths |
|---------|-------|
| `pull_request` | any |
| `push` to `main` | `crates/benchora/harbor-soft/**` |

**Soak clock starts** on the first `main` push after this suite lands. Count only runs where
job `Harbor eval stub (corpus preflight)` completes with stub pass (log contains
`STUB PASS: corpus valid`).

## Phase 3 soak checklist

Track in PR comments or [`audit/harbor-phase3-soak-log.md`](../audit/harbor-phase3-soak-log.md)
until Phase 4 maintainer sign-off:

- [ ] Seven consecutive `main` workflow runs green for `harbor-eval-stub-soft.yml` (no stub regressions).
- [ ] No merged PRs broke sharecli `scripts/eval/run-corpus.sh` preflight on `main` during the window.
- [x] `harbor_soak.sh` reproduces CI locally on branch HEAD (execution scaffold).
- [ ] Cross-repo pins table above filled with recorded portage / pheno-harness refs.
- [ ] Maintainer acknowledges Phase 3 complete — **does not** mark ADR 0002 superseded (Phase 4).

## Execution scaffold

| Artifact | Path | Role |
|----------|------|------|
| Local parity runner | `scripts/harbor_soak.sh` | Runs stub + corpus preflight; optional log append |
| Checklist log template | `audit/harbor-phase3-soak-log.md` | Seven `main` run rows + pin table |
| CI soft job | `workflows/harbor-soak-exec-soft.yml` | PR/push parity (`continue-on-error`) |

```bash
export SHARECLI_ROOT=/path/to/sharecli
bash scripts/harbor_stub.sh
# optional: append a local parity row to the checklist log
BENCHORA_HARBOR_SOAK_LOG=audit/harbor-phase3-soak-log.md \
  BENCHORA_HARBOR_SOAK_SOURCE=local \
  bash scripts/harbor_soak.sh
```

**Partial evidence:** execution scaffold on disk; seven-day `main` soak window
remains open post-merge. L76 stays **1** until checklist row 7 is green on `main`.

## Local parity

```bash
export SHARECLI_ROOT=/path/to/sharecli
bash scripts/harbor_stub.sh
bash scripts/harbor_soak.sh
```

Expected stub tail:

```
STUB PASS: corpus valid; Harbor task runner not wired (Phase 2 soft)
Harbor/portage-temp env provisioning deferred — see docs/harbor-phase3-soak.md
```

Soak scaffold tail:

```
SOAK SCAFFOLD PASS: local stub + corpus preflight green (Phase 3 partial)
```

## Phase map (ADR 0005)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 0 | Supervisor corpus + ADR 0002 | Done |
| 1 | ADR 0005 supersede plan | Done |
| 2 | [`harbor-eval-stub.md`](./harbor-eval-stub.md) + `harbor_stub.sh` | Done (soft) |
| **3** | **This doc + seven-day soft soak on `main`** | **In progress (scaffold landed)** |
| 4 | Mark ADR 0002 superseded; GOVERNANCE + lane re-score | Deferred |

## Audit evidence (C08 L76)

| Line | Evidence | Score |
|------|----------|-------|
| **L76** Agent-eval pipeline | ADR 0002 N/A seed; ADR 0005 Phase 2 stub; **this soak plan**; `harbor-eval-stub-soft.yml` | **1** — unchanged until soak completes + Phase 4 |

**Soft follow-up**

| Item | Status |
|------|--------|
| Harbor Phase 3 soak evidence plan | Done (this file) |
| Harbor Phase 3 soak execution scaffold | Done (`harbor_soak.sh` + checklist log + soft CI) |
| Seven-day green soak on `main` | Open — **0/7 complete · 7 remaining** (local soft L1 2026-07-19 recorded; does not count) |
| Record portage / pheno-harness pins in soak PR | Open — see portage `docs/ops/harbor-env-pins*.md` |
| Mark ADR 0002 superseded | Deferred (Phase 4) |

**Status:** Phase 3 soak IN_PROGRESS · **FR:** FR-003 traceability · **Last sync:** 2026-07-19
