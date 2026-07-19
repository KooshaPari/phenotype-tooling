# Benchora

Absorb home for Phenotype **perf harness** and **Harbor soft-eval suite** layers
(on top of existing eval suites).

| Layer | Location | Owns |
|-------|----------|------|
| Suite soft surface | `harbor-soft/` | Stub/soak scripts, soft CI workflows, soak docs/audit |
| Harbor fork / env | [KooshaPari/portage-temp](https://github.com/KooshaPari/portage-temp) | Harbor provisioning, env pins, task runners |
| Supervisor corpus | sharecli (external) | `docs/eval/corpus` + `scripts/eval/run-corpus.sh` |

**sharecli no longer owns Harbor soft CI.** Suite-facing soft workflows and docs
live here; Harbor environment work belongs in portage-temp.

## Workspace membership

This crate is listed in the phenotype-tooling root `[workspace].members` as
`crates/benchora`.

## Quick pointers

- Soft Harbor suite: [`harbor-soft/README.md`](./harbor-soft/README.md)
- Harbor env pins (portage): see portage `docs/ops/harbor-env-pins*.md`
- Related crate: `crates/perfharness` (3-regime profiling harness)
