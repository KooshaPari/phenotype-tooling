# Branch Protection Rules (Main)

> Documentation companion for `.github/branch-protection/main.json`.
> The JSON file is the source of truth; this Markdown is the human-readable
> summary + apply instructions.

## Required Status Checks

| Check | Job role |
|---|---|
| `lint / fmt` | `cargo fmt --all -- --check` |
| `lint / clippy` | `cargo clippy --workspace --all-features -- -D warnings` |
| `build / check` | `cargo check --workspace --all-features` |
| `test / unit` | `cargo test --workspace --all-features --no-fail-fast` |
| `ptx / governance` | `ptx --strict --manifest ptx.ci.toml` |
| `bench / regression` | `bench_diff.py` against `BENCHMARKS.md` (5% threshold) |
| `audit / cargo-deny` | License, advisory, sources check |
| `audit / trufflehog` | Verified-secret filesystem scan |
| `scorecard / openssf` | OpenSSF Scorecard badge |

`strict: true` means a PR must be **up to date with `main`** before any
required check can succeed.

## Pull Request Review Rules

- `required_approving_review_count: 1`
- `dismiss_stale_reviews: true` (push after approval resets the review)
- `require_code_owner_reviews: true` (CODEOWNERS file enforced)
- `require_last_push_approval: true` (last push must be re-approved)

## Branch Behavior

| Setting | Value |
|---|---|
| `enforce_admins` | `true` — even admins can't merge without checks |
| `required_linear_history` | `true` — rebase/squash only, no merge commits |
| `required_signatures` | `true` — every commit on `main` must be GPG/SSH signed |
| `allow_force_pushes` | `false` |
| `allow_deletions` | `false` |
| `required_conversation_resolution` | `true` |
| `block_creations` | `false` |

## How to apply

The file `.github/branch-protection/main.json` is the declarative payload.
To install on the repo:

```bash
# One-time. Idempotent — running it twice produces the same end state.
gh auth login --scopes admin:repo,repo
bash scripts/apply_branch_protection.sh
```

To tighten any rule (e.g. bump required reviewers to 2), edit the JSON,
re-run. To add a new required check:

1. Add the workflow to `.github/workflows/<name>.yml` with an
   explicit `name:` matching the desired context.
2. Append the context to `required_status_checks.contexts` in the JSON.
3. Run `bash scripts/apply_branch_protection.sh`.

## Why `ptx` is a Required Check

PTX is the local governance harness. Promoting it to a GitHub Actions
required check means a PR that breaks a `ptx.ci.toml` rule cannot be
merged even if a casual reviewer rubber-stamps. Combined with
`require_code_owner_reviews`, the merge-gate becomes:

1. CI checks pass (including ptx).
2. CODEOWNER(s) approve.
3. Linear history preserved.
4. Signed commits only.

This is the WP-14 acceptance criteria.
