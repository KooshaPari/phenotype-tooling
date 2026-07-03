# WP-14: Branch protection + PTX as required check

## Goal

Promote `ptx` from an advisory on-call surface to a **merge-gate**.
Every PR against `main` must pass the PTX governance manifest before
reviewers can merge; `main` itself becomes a protected branch with
strict linear history, signed commits, and dismiss-stale reviews.

## Deliverables

| File | Purpose |
|---|---|
| `.github/branch-protection/main.json` | Declarative branch-protection payload |
| `scripts/apply_branch_protection.sh` | `gh api` applier (idempotent) |
| `.github/workflows/ptx-gate.yml` | New `ptx / governance` required check |
| `ptx.ci.toml` | Default governance manifest for CI |
| `docs/WP-14-BRANCH-PROTECTION.md` | This adoption guide |

## Branch protection rules

| Rule | Setting |
|---|---|
| Required status checks | `lint / fmt`, `lint / clippy`, `build / check`, `test / unit`, `ptx / governance`, `bench / regression`, `audit / cargo-deny`, `audit / trufflehog`, `scorecard / openssf` |
| Require branches up to date | `strict: true` |
| Require review approval count | `1` |
| Dismiss stale reviews on push | `true` |
| Require code owner review | `true` |
| Require last push approval | `true` |
| Enforce for administrators | `true` |
| Required linear history | `true` |
| Required signed commits | `true` |
| Block force pushes | `true` |
| Block deletions | `true` |
| Require conversation resolution | `true` |

## Required-check rationale

| Check | Job role |
|---|---|
| `lint / fmt` | Catches `cargo fmt --check` drift early |
| `lint / clippy` | Style + correctness + pedantic nits |
| `build / check` | Cross-target type-check |
| `test / unit` | Functional correctness |
| `ptx / governance` | Phenotype-specific gates (extracted by PTX) |
| `bench / regression` | Performance budget enforcement |
| `audit / cargo-deny` | License + advisory + sources |
| `audit / trufflehog` | Secret scanning |
| `scorecard / openssf` | Supply-chain hygiene |

The **first four** are universally recognized CI primitives and run
on every PR. The **last five** are the WP-3 → WP-12 outputs that
turn the platform from "passes cargo" into "passes the governance
checklist".

## Apply the rules

```bash
# One-time application. Idempotent.
gh auth login --scopes admin:repo,repo
bash scripts/apply_branch_protection.sh
```

To relax any field, edit `.github/branch-protection/main.json`,
re-run the script. The script asserts admin:repo scope is held by the
caller.

## Required-check: `ptx / governance`

The `.github/workflows/ptx-gate.yml` workflow runs `ptx --strict`
on a checked-in `ptx.ci.toml` manifest. The manifest is the same
one operators use locally for `ptx run`; CI just enforces it on
every PR.

```bash
# Local parity check before pushing:
cargo run -p ptx -- --manifest ptx.ci.toml --report-out /tmp/ptx.md
```

If ptx exits non-zero, the PR is blocked. The full markdown report
uploads as artifact `ptx-governance-report`.

## Acceptance criteria

- [ ] Branch protection applied (verified via `gh api ... | jq`)
- [ ] `ptx / governance` job is "Required" in branch-protection UI
- [ ] PR against a test branch fails to merge if ptx fails
- [ ] PR against `main` from a forked repo still requires ptx (because
      GitHub-runs the workflow on PR and surfaces as required check)
- [ ] Force-push to `main` blocked
- [ ] Linear-history merge (squash or rebase) enforced
- [ ] Administrator enforcement enabled

## Customization

To add a new required check:

1. Add the workflow file under `.github/workflows/`
2. Append the job name to `required_status_checks.contexts` in
   `.github/branch-protection/main.json`
3. Run `bash scripts/apply_branch_protection.sh`
4. Verify in GitHub branch-protection UI
