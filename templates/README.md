# Phenotype Shared Boilerplate Templates

Drop-in boilerplate files for the 124 audited repos. Each file is **pure content** — no Jinja, no placeholders, no symlinks, no scripts. Copy verbatim and commit.

## Files

| File | Purpose | Used by (5+ repos) |
|------|---------|--------------------|
| `CODEOWNERS` | Owner-of-everything marker. | AgilentCloud, AlphaScan, AuthKit, BytePort, CodeFurnace, DataKit, … (70/82 repos) |
| `editorconfig` | Phenotype org canonical EditorConfig (UTF-8, LF, indent 4 / 2, Markdown trailing-space). | chatta, focalpoint, localbase3, portage, phenotype-tooling, … (22 repos) |
| `cliff.toml` | git-cliff + Keep-a-Changelog release config. | focalpoint, focalpoint-iOS, focalpoint-CLI, melosviz, AgilePlus, … (33/48 repos) |
| `gitignore-rust` | Rust-only: Cargo, toolchains, secrets, VSCode allowlist. | chatta, byteport, kodepp, kodeml, koderunner, … (all pure-Rust repos) |
| `gitignore-python` | Python-only: venvs, bytecache, coverage, secrets, VSCode allowlist. | agent-devops-setups, agents-config, dataspec, helio, kwatch, … (all pure-Python repos) |
| `gitignore-node` | Node/TS-only: node_modules, tsc, turbo, secrets, VSCode allowlist. | chatta-web, loupe, thegent-app, docsite-skeleton, … (all pure-Node repos) |
| `gitignore-ios` | Xcode/iOS-only: DerivedData, SwiftPM, CocoaPods, secrets, VSCode allowlist. | focalpoint-iOS, helmet-ios, melosviz-ios, kdesktopvirt-ios, … (all pure-iOS repos) |
| `gitignore-mixed-rust-ios` | **Dominant family** (52/124). Rust + iOS union. | focalpoint, kdesktopvirt, melosviz, byteport-ios, kodepp-ios, … |
| `gitignore-mixed-rust-node` | Rust + Node union. | portage, localbase3, agent-orchestrator, traitors, … |
| `gitignore-mixed-python-node` | Python + Node union. | agent-devops-setups, agents-config, sidekick, dataspec, … |

## Common long-tail patterns preserved in every gitignore

- `!.env.example` / `!.env.sample` — keep sample configs, ignore real secrets
- `**/secrets.*` with `!**/secrets.example` — long-tail secret allowlist
- `/.vscode/*` allowlist — keep `extensions.json`, `settings.json`, `launch.json`, `tasks.json` only
- `/kitty-specs/.worktrees/` — ignore spec-kitty working trees
- `Thumbs.db`, `*.swp`, `*.swo`, `*~`, `[Bb]in/`, `*.exe` — Windows / swap / editor artifacts
- `Cargo.lock.bak`, `*.moved-aside`, `*.dSYM` — ecosystem-specific long tails

## Adoption

```bash
# from a target repo
cp /Users/kooshapari/CodeProjects/Phenotype/repos/phenotype-tooling/templates/CODEOWNERS .
cp /Users/kooshapari/CodeProjects/Phenotype/repos/phenotype-tooling/templates/editorconfig .editorconfig
# pick the right gitignore family from the table above
```

No generator. No template engine. No symlinks. Each file is exactly the bytes you would hand-write.
