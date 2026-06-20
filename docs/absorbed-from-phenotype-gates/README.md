<!-- AI-DD-META:START -->
<!-- This repository is planned, maintained, and managed by AI Agents only. -->
<!-- Slop issues are expected and intentionally present as part of an HITL-less -->
<!-- /minimized AI-DD metaproject of learning, refining, and building brute-force -->
<!-- training for both agents and the human operator. -->
![Downloads](https://img.shields.io/github/downloads/KooshaPari/phenotype-gates/total?style=flat-square&label=downloads&color=blue)
![GitHub release](https://img.shields.io/github/v/release/KooshaPari/phenotype-gates?style=flat-square&label=release)
![License](https://img.shields.io/github/license/KooshaPari/phenotype-gates?style=flat-square)
![AI-Slop](https://img.shields.io/badge/AI--DD-Slop%20Expected-orange?style=flat-square)
![AI-Only-Maintained](https://img.shields.io/badge/Planned%20%26%20Maintained%20by-AI%20Agents%20Only-red?style=flat-square)
![HITL-less](https://img.shields.io/badge/HITL--less%20AI--DD-metaproject-yellow?style=flat-square)

> ⚠️ **AI-Agent-Only Repository**
>
> This repo is **planned, maintained, and managed exclusively by AI Agents**.
> Slop issues, rough edges, and AI artifacts are **expected and intentionally
> present** as part of an **HITL-less / minimized AI-DD** metaproject focused
> on learning, refining, and brute-force training both the agents and the
> human operator. Bug reports and contributions are still welcome, but please
> expect AI-generated code, comments, and documentation throughout.
<!-- AI-DD-META:END -->
# phenotype-gates
Policy-as-code gate engine for the Phenotype org

## Quickstart

```sh
npm install
./bin/just demo
```

`just demo` runs the minimal end-to-end self-test (issue #2):

1. `gates check .` — self gates pass
2. `gates check bench/fixture` — exits 1 with `FR-PGAT-008: action foo/bar must be pinned SHA, got @v4`
3. `gates fix --gate=FR-PGAT-008` — prints suggested patch and pins the SHA
4. re-run check exits 0; `gates.lock.json` updated

## Layout

- `src/engine.js` — gates engine (TOML/serde-style validated `gates.yml`)
- `src/cli.js` — `gates` CLI (`check`, `fix`, `version`)
- `gates.yml` — self policy (FR-PGAT-001)
- `bench/fixture/` — fixture repo with deliberate unpinned `foo/bar@v4`
- `bench/e2e/demo.js` — full e2e orchestrator
- `bin/just` — minimal `just` shim
- `justfile` — `demo` recipe
