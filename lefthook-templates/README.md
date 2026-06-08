# AI-DD Hook & Task Templates

Reusable templates for AI-DD-grade pre-commit/pre-push hooks and CI quality
gates. Generated once and stamped into every repo in the Phenotype org.

## Files

| File | Purpose |
|------|---------|
| `lefthook.yml.tpl` | lefthook config (pre-commit + pre-push). Strict, fails loud. |
| `Taskfile.yml.tpl` | Taskfile with the `quality-gate` task per `AgilePlus/docs/ai-dd-governance.md` §1. |

Both files are Go-template style with one placeholder: `{{REPO_NAME}}`.

## Install into a target repo

```bash
# 1. Copy the templates
cp lefthook.yml.tpl /path/to/target/lefthook.yml
cp Taskfile.yml.tpl /path/to/target/Taskfile.yml

# 2. Substitute the repo name
sed -i '' 's|{{REPO_NAME}}|your-repo-name|g' \
  /path/to/target/lefthook.yml \
  /path/to/target/Taskfile.yml

# 3. Install the lefthook git hooks
cd /path/to/target && lefthook install

# 4. Install the runtime tools (one-time per dev machine)
brew install actionlint gitleaks trufflehog
pipx install ruff
cargo install cargo-deny cargo-geiger cargo-tarpaulin
```

## What gets enforced

**`lefthook.yml`** — runs on every commit (fast) and push (heavier):

- `ruff check` + `ruff format --check` on staged Python
- `cargo fmt --check` + `cargo check --workspace` on staged Rust
- `actionlint` on staged workflow YAML
- `gitleaks` (preferred) or `trufflehog` (fallback) on staged files
- Pre-push: `cargo test --no-run` and full-`actionlint`

**`Taskfile.yml`** — `task quality-gate` runs the eight AI-DD §1 tasks:
`lint`, `type-check`, `test`, `audit-secrets`, `drift-check`,
`anti-pattern-scan`, `libification-scan`, `traceability-verify`.

## Strictness policy

Per `AgilePlus/docs/ai-dd-governance.md` §1, every hook **fails loudly** when
a tool is missing. There are no silent fallbacks. If a tool is required by
the gate, install it — or block the PR until you do.

## Source

- Templates: `phenotype-tooling/lefthook-templates/`
- Governance: `AgilePlus/docs/ai-dd-governance.md`
