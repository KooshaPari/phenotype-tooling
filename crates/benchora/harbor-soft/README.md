# Harbor soft (suite-facing)

Extracted from sharecli **C08 soft Harbor** surface. **Suite-facing only.**

| Concern | Home |
|---------|------|
| Soft stub / soak scripts + workflows | **this tree** (`crates/benchora/harbor-soft`) |
| Harbor fork / env provisioning | [KooshaPari/portage-temp](https://github.com/KooshaPari/portage-temp) |
| Supervisor corpus preflight | sharecli (`SHARECLI_ROOT` required) |

**sharecli no longer owns Harbor soft CI.** Soft workflows under `workflows/` are
suite-layer references; wire them from phenotype-tooling (or absorb consumers),
not from sharecli.

## Layout

```
harbor-soft/
  scripts/     harbor_stub.sh, harbor_soak.sh
  workflows/   harbor-eval-stub-soft.yml, harbor-soak-exec-soft.yml
  docs/        harbor-eval-stub.md, harbor-phase3-soak.md
  audit/       harbor-phase3-soak-log.md
```

## Local run

```bash
# Corpus preflight requires SHARECLI_ROOT pointing at a sharecli checkout
export SHARECLI_ROOT=/path/to/sharecli
bash scripts/harbor_stub.sh
bash scripts/harbor_soak.sh
```

If `SHARECLI_ROOT` is unset, scripts fail loudly (exit 2) — no silent degrade.
