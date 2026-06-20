# pheno-llms-txt — SPEC

## Scope

Canonical generator for [`llms.txt`](https://llmstxt.org) files (the LLM-friendly
README proposed at llmstxt.org). Used by every pheno-* repo to ship a
≤200-line model-card that an LLM can consume in full in one context window.

Implements V4 §70.3 + §77.2 of `FLEET_100TASK_DAG_V4.md`.

## Public API

- `class LlmConfig` — dataclass with 7 fields:
  `repo_name`, `tagline`, `install`, `usage`, `public_api`, `common_errors`, `references`.
- `render(config: LlmConfig) -> str` — render the canonical llms.txt template.
- `load_config(path: Path) -> LlmConfig` — read a `pheno-llms-txt.yaml` from disk.
- `write_llms_txt(config: LlmConfig, dest: Path) -> None` — render + write atomically.
- `init_llms(repo_dir: Path | str) -> dict` — V6 PR-3 scaffold-kit entrypoint:
  bootstrap a starter config + render llms.txt; idempotent.

## CLI

```
pheno-llms-txt                 # writes ./llms.txt from ./pheno-llms-txt.yaml
pheno-llms-txt --out docs/llms.txt
```

## Conventions

- **When to use:** every pheno-* repo must ship an llms.txt.
- **When NOT to use:** non-pheno-* repos (write a README only).
- **5-line quickstart:**
  ```python
  from pathlib import Path
  from pheno_llms_txt import LlmConfig, render, write_llms_txt
  cfg = LlmConfig(repo_name="my-repo", tagline="One-liner.",
                  install=["pip install my-repo"], usage=["my-repo --help"])
  write_llms_txt(cfg, Path("llms.txt"))
  ```

## Output contract

- 30-80 lines (well under the 200-line cap from §77.2).
- Sections: Install, Usage, Public API, Common errors, See also.
- `common_errors` is a list of `[error_message, fix]` pairs.

## Quality bar

- 71-pillar score: 24/71 (Tier 0)
- Test matrix: 3+ smoke tests in `tests/`
- Coverage: pending measurement
- License: dual (MIT + Apache-2.0)

## See also

- ADR-023 (Rule 3.1 substrate quality bar)
- V4 §77.2 (llms.txt crutch adoption)
- https://llmstxt.org (the spec)