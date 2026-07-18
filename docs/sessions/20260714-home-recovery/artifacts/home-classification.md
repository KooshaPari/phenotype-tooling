# Home Classification Reconciliation

## Live Inventory

The current first-level inventory contains **408** entries: **335 hidden** and **73 visible**.
This supersedes the initial 411-entry snapshot for live arithmetic, but does not erase the
baseline. Exact parsing of the baseline and current inventories proves that
`~/CLIProxyAPI` and `~/router-rb-2c` disappeared externally during the audit. The identity
of the third entry in the 411-to-408 difference remains unresolved.

| Disposition | Count |
|---|---:|
| `KEEP_HOME` | 239 |
| `KEEP_REVIEW` | 120 |
| `REPO_INTEGRATE` | 10 |
| `REPO_RELOCATE` | 2 |
| `WORKTREE_RECOVER` | 1 |
| `QUARANTINE_PRIVATE` | 15 |
| `ARCHIVE_EXTERNAL` | 21 |
| **Live total** | **408** |

Arithmetic: `239 + 120 + 10 + 2 + 1 + 15 + 21 = 408`.

## Candidate Groups and Paths

### Repository integration (10)

- `~/evals_only_tests`
- `~/pheno_shell_only_tests`
- `~/phench`
- `~/plugins`
- `~/scripts`
- `~/src`
- `~/superpowers`
- `~/temp-PRODVERCEL`
- `~/uvloop_pkg`
- `~/winterminal_check`

These are loose source or repository-shaped content. Compare them against canonical
repositories, preserve unique content on named branches, and verify a remote ref before
removing any home copy.

### Repository relocation (2 owning first-level entries)

- `~/Repos` owns 11 nested repositories: `template-commons`, `znap`, `heliosCLI`, `civ`,
  `phenotypeActions`, `phenodocs`, `phench`, `phenotype-infrakit`, `phenotype-design`,
  `phenotype-shared`, and `phenotype-go-kit`.
- `~/forge` owns a nested `AgilePlus` repository.

Relocate only after per-repository topology, dirty-state, upstream, and remote-reachability
checks. The owning first-level count is two; the nested repository count is twelve.

### Worktree recovery (1 owning first-level entry)

- `~/CodeProjects` owns the `Phenotype-v16` Git-file worktree and therefore requires
  topology-aware recovery rather than ordinary directory relocation.

### Private quarantine (15)

- `~/.aws`
- `~/.boto`
- `~/.claude-imessage.env`
- `~/.cloudflare-global-key`
- `~/.cloudflare-token`
- `~/.env`
- `~/.git-credentials`
- `~/.gnupg`
- `~/.kube`
- `~/.oci`
- `~/.pulumi`
- `~/.sentryclirc`
- `~/.ssh`
- `~/.upstash.json`
- `~/.vault-token`

These paths are credential- or identity-bearing. Preserve through an encrypted secret or
backup system, never a normal Git source branch, and never copy values into audit output.

### External archive (21)

- `~/0e546...png` (the baseline report abbreviated the content-addressed filename)
- `~/2026-05-23-melosviz-scope-v0.1-draft.md`
- `~/2026-05-25_21-43-03`
- `~/2026-05-25_21-43-04`
- `~/2026-05-25_21-43-05`
- `~/2026-05-25_21-43-06`
- `~/2026-05-25_21-43-15`
- `~/2026-07-13_18-11-29`
- `~/2026-07-13_18-12-06`
- `~/2026-07-13_22-06-02`
- `~/2026-07-13_22-06-16`
- `~/2026-07-13_22-06-21`
- `~/Archives`
- `~/audit`
- `~/claude-session-audit-Feb1-Mar3-2026.md`
- `~/iMovie Library.imovielibrary`
- `~/Koosha Paridehpour Resume-17.pdf`
- `~/logs`
- `~/notes`
- `~/repos.md`
- `~/soul.md`

Archive with hashes, original names, and encrypted or large-object-capable remote evidence.

### Keep-review exemplars (part of the 120-entry class)

The reconciled classification contains 120 `KEEP_REVIEW` entries. The completed report
called out the following paths and groups for owner review rather than relocation:

- two zero-byte filenames containing embedded newlines and beginning with `%sn`;
- `~/1`, `~/Applications`, `~/Dev Environment`, `~/docs`, `~/FLEET_DAG.db`, `~/forge.db`,
  `~/forge_tmp`, `~/forge_tmp_triage.py`, `~/governance`, `~/IdeaProjects`, `~/intent`,
  `~/javafx-sdk-21.0.4`, `~/JFX`, `~/llm-models`, `~/merge-docs-prs.sh`, `~/patch_vllm.py`,
  `~/restore-thegent-bins.sh`, `~/tmp`, `~/Users`, `~/work`, and `~/~` (literal child `~`);
- 72 hidden code-like entries and 26 hidden backup-like entries, retained as review groups
  because their exact escaped path ledger was not included in the synthesis handoff.

The grouped counts overlap the named exemplars in the source report and must not be added
to derive a second total. The authoritative count is the reconciled 120-entry disposition.
No review candidate is authorized for deletion.

## Externally Missing Baseline Paths

- `~/CLIProxyAPI`: absent now. Its unique abbreviated baseline commit `f5cbb192` is absent
  from the inspected canonical and Airlock object stores, but is remotely backed up as
  `f5cbb192222dab78b710a8b94188fbf456232830` at
  `refs/heads/koosha/security-and-test-coverage-policy` in
  `KooshaPari/cliproxyapi-plusplus`, verified with `git ls-remote`.
- `~/router-rb-2c`: absent now. At baseline it was clean and tracking `origin/main` for
  `KooshaPari/phenotype-router`; the exact baseline HEAD was not captured.
- Third discrepancy: unresolved. Do not infer deletion or identity without new evidence.

## Preservation Rule

No classification is a deletion instruction. Integrate, relocate, recover, quarantine, or
archive only after identity, secret/size assessment, stable commit or archive identifier,
independent remote verification, restoration check, and source-to-destination manifest.
