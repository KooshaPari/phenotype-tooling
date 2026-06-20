# pheno-llms-txt

> Generate [`llms.txt`](https://llmstxt.org) files for Phenotype repos (LLM-friendly README).

This is the canonical implementation of the **`pheno-llms-txt`** AI-DD crutch
described in `FLEET_100TASK_DAG_V4.md` §70.3 + §77.2. Every focus repo in the
Phenotype fleet adopts it as part of V11 L16 AX (Agent eXperience).

## What it does

Generates a ≤200 line `llms.txt` file (the LLM-friendly README proposed at
[llmstxt.org](https://llmstxt.org)) by rendering a template with sections:
Install, Usage, Public API, Common errors, See also.

## Install

```bash
pip install pheno-llms-txt
```

## Usage

```bash
# 1. Drop a config in your repo root (optional):
cat > pheno-llms-txt.yaml <<'YAML'
repo_name: thegent
tagline: "Agent orchestration CLI for KooshaPari's thegent."
install:
  - pip install thegent
usage:
  - "thegent --help"
  - "thegent worker dispatch 'summarize this PR'"
public_api:
  - thegent.cli::main
  - thegent.worker::dispatch
common_errors:
  - ["Error: API key not set", "export THEGENT_API_KEY=..."]
references:
  - https://github.com/KooshaPari/thegent
  - FLEET_100TASK_DAG_V4.md §70.3
YAML

# 2. Run:
pheno-llms-txt
# → Wrote llms.txt
```

## What gets generated

A 30–80 line `llms.txt` (well under the 200-line cap from §77.2) with:

- **Install** — 1-5 install commands
- **Usage** — 1-5 example invocations
- **Public API** — top 30 public symbols
- **Common errors** — error → fix pairs
- **See also** — 1-5 references

## Reference template (excerpt)

```
# llms.txt — thegent

> Agent orchestration CLI for KooshaPari's thegent.

## Install
```
pip install thegent
```

## Usage
```thegent --help```
```thegent worker dispatch 'summarize this PR'```

## Public API
- `thegent.cli::main`
- `thegent.worker::dispatch`

## Common errors
- `Error: API key not set`: export THEGENT_API_KEY=...

## See also
- https://github.com/KooshaPari/thegent
- FLEET_100TASK_DAG_V4.md §70.3
```

## Eat your own dogfood

This repo uses itself. See [`llms.txt`](llms.txt) and [`AGENTS.md`](AGENTS.md).

## License

MIT
