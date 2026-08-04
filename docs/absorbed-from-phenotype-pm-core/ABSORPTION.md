# phenotype-pm-core provenance hold

**Status:** `PRESERVE_ONLY` / `NOT_ABSORBED`

This record corrects the historical absorption note without importing source
files. `phenotype-pm-core` remains a live, non-fork parent candidate. No merge,
archive, retirement, deletion, reset, or force-push is authorized by this
manifest.

## Source boundary

- **Source:** `KooshaPari/phenotype-pm-core`
- **Source URL:** <https://github.com/KooshaPari/phenotype-pm-core>
- **Default branch:** `master`
- **Default tip at capture:** `d3277c4049c85eeafa12f7939d8fca90e92a969f`
- **Captured:** `2026-08-04T06:42:45Z`
- **Remote state:** live, non-fork; source refs remain authoritative

Read-only source branch inventory captured with `git ls-remote --heads`:

| Branch | Tip |
|---|---|
| `audit/pmcore-v2` | `f45b540acb600d3284b1aa5bc22d1526529a41d1` |
| `chore/adr-versioning` | `2c65aca2025726f8725620e63ef86170917ac8d3` |
| `dependabot/cargo/regex-1.13.1` | `afe521f1d570b623574d0066c79a5d073ca5c575` |
| `dependabot/cargo/serde_json-1.0.151` | `96378a4c81bc9b70b0f0c5128520878b94785864` |
| `dependabot/github_actions/actions/dependency-review-action-5` | `41ee74b8699f7b5ecd24a39204841f4fa6a6e5a1` |
| `dependabot/github_actions/actions/setup-go-7` | `2872bf37bb090f3fc1ef0fcf5548d07d8d6ea598` |
| `dependabot/github_actions/actions/setup-node-7` | `8d27eea5824b593c30646eda393251cd170a7c00` |
| `dependabot/github_actions/actions/setup-python-7` | `333c0a7102d6e653e4a2dd249ee864792677e2c3` |
| `dependabot/github_actions/actions/upload-artifact-7` | `a8d8b5d13ffb797bbc629fe26c479b283b3a4574` |
| `feat/execution-graph` | `d5f27f777af57fde0ee241e804f1c4587b365b7c` |
| `feat/trace-gate-pipeline` | `a85c96470cb231fad2d3558e56ca24cd9ceb7884` |
| `fix/trace-gate-yaml-syntax` | `1437a42af7171f726f923548936ba29af1652ec4` |
| `master` | `d3277c4049c85eeafa12f7939d8fca90e92a969f` |

## Target comparison

- **Target:** `KooshaPari/phenotype-tooling`
- **Target base:** `main` at `3b952d66267c06ec5a68e2c4b0a37ac6a59a4e47`
- **Proposed target path:** `crates/pm-core/`
- **Target path at base:** absent
- **Source tip reachability:** not established; no source files are imported
- **Parity:** `NOT VERIFIED` (no commit, API, test, or dependency parity claim)

The existing `docs/absorbed-from-phenotype-pm-core/` path is retained only as
the registry's established documentation convention. It is not evidence that
the source was absorbed or deleted.

## Required next gates

1. Preserve the complete source refs in an independently restorable bundle.
2. Compare source trees, APIs, tests, and dependency contracts with any
   proposed `phenotype-tooling/crates/pm-core/` import.
3. Land a separate source-bearing import PR only after parity evidence and
   review; keep this hold until then.
4. Do not archive or retire the source until dual-cloud preservation,
   independent restore, and sponsor ACK are all recorded.
