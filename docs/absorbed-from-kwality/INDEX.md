# Absorbed from KooshaPari/kwality — full retirement

This directory is the **complete archival absorption** of
[`KooshaPari/kwality`](https://github.com/KooshaPari/kwality) (the LLM
Validation & Quality Assurance Platform) into the Phenotype tooling
monorepo. Source repository status: **scheduled for archival + delete** per
kilo audit #144 and the 2026-06-18 retirement decision.

> **Historical reference only.** Kwality is preserved here as a research
> artifact. It is not built, tested, or shipped as part of
> `phenotype-tooling`. See [`RETIREMENT.md`](./RETIREMENT.md) for the full
> architecture retirement decision.

## Layout

```
docs/absorbed-from-kwality/
├── ADR.md / ADRS.md                Architectural decision records (single + batch)
├── AGENTS.md                       Agent operating instructions (legacy)
├── ARCHITECTURE.md                 245-line architecture doc
├── CHARTER.md                      Project charter
├── CHANGELOG.md                    627-line Keep-a-Changelog format history
├── CLAUDE.md                       Claude-specific guidance (legacy)
├── FUNCTIONAL_REQUIREMENTS.md      10-line condensed requirements
├── ORIGINAL_README.md              Preserved verbatim from source repo
├── PLAN.md                         137-line implementation plan
├── PRD.md                          878-line product requirements doc
├── PRODUCTION-READINESS-SUMMARY.md Production readiness assessment
├── README.md                       (created by PR #157) branch-only absorb note
├── RETIREMENT.md                   Architecture retirement decision (this PR)
├── review.md                       21-line review notes
├── SECURITY.md                     Top-level security posture
├── SOTA.md                         1510-line state-of-the-art sweep
├── SPEC.md                         2810-line canonical specification
├── VERSION                         Build version (single line)
├── WORKLOG.md / worklog.md         Worklog (both casings preserved)
├── intent.md                       19-line intent statement
├── .gitignore / .env.example       Build configuration
├── go.mod / go.sum                 Go module dependencies (pinned)
├── database/
│   ├── neo4j/                      Cypher scripts + Neo4j config
│   └── schema/                     Graph + SQL schema definitions
├── demos/
│   ├── *.tape                      VHS tape scripts (6 files)
│   ├── generate-demos.sh           VHS generation script
│   └── README.md                   Demo instructions (GIFs excluded — see RETIREMENT.md)
├── docs/
│   ├── architecture/               Deep architecture docs
│   ├── intent/                     Intent hierarchy
│   ├── sota/                       State-of-the-art sub-sweeps
│   ├── worklogs/                   Per-day worklog snapshots
│   ├── deployment-guide.md         Generic deployment guide
│   ├── PRODUCTION-DEPLOYMENT-GUIDE.md
│   └── PRODUCTION-SECURITY-GUIDE.md
├── examples/
│   ├── config/                     Sample kwality.toml / config files
│   └── usage/                      Usage examples
├── src/
│   ├── cmd/                        Main entry points (kwality, kwality-cli)
│   ├── engines/                    LLM adapters (DeepEval, Playwright MCP, Neo4j)
│   ├── internal/                   Internal packages
│   └── scripts/                    Build + ops scripts
└── tests/
    ├── integration/                Integration test suite
    └── playwright/                 Playwright browser tests
```

## What's NOT included (intentionally excluded)

| Path | Reason | Size |
|---|---|---|
| `bin/kwality` / `bin/kwality-cli` | Compiled binaries | 25 MB |
| `kwality/` / `kwality-cli/` (top level) | Pre-built release artifacts | 25 MB |
| `memory/` | Runtime session cache (sqlite) | 2.7 MB |
| `.hive-mind/` | Compiled hive-mind cache | ~1 MB |
| `demos/*.gif` | Demo recordings | 5.9 MB |
| `demos/*.tape` → **included** | VHS source scripts (small, regenerable) | <10 KB |
| `.git/` | Git internals | 20 MB |

These are either compiled artifacts, runtime caches, or media files that
do not belong in a reference archive. The `demos/*.tape` scripts are
included because they regenerate the GIFs via VHS.

## Origin provenance

### From PR #157 (commit 311bdd0, by `kilo-bot@koosha-pari.com`)

10 files extracted from branch-only artifacts on `KooshaPari/kwality` topic
branches. These existed on topic branches but were never merged to
`kwality/main`. See the in-tree `README.md` for the per-file origin branch
mapping.

### From this PR (2026-06-18, retirement commit)

83 additional files extracted from `KooshaPari/kwality` main branch at the
v0.x.x tag (HEAD commit hash preserved in `VERSION` and the commit log of
the absorption PR). Includes:

- All governance docs (SPEC, PRD, SOTA, ARCHITECTURE, CHARTER, ADR, etc.)
- All source code (engines, internal, scripts, cmd)
- All tests (integration, playwright)
- All examples (config, usage)
- Database artifacts (neo4j scripts + schema)
- Demo source (VHS tapes + generation script, GIFs excluded)
- Build config (go.mod, go.sum, .gitignore, .env.example)

## Extraction date

2026-06-18 (this PR) + 2026-06-18 (PR #157 baseline)