# .editorconfig Adoption Guide

## TL;DR
Replace your `.editorconfig` with the canonical template at
[`templates/.editorconfig`](https://github.com/KooshaPari/phenotype-tooling/blob/main/templates/.editorconfig).
For 90%+ of repos, this is the entire change.

## When you need more
Add per-extension rules BELOW the `[*]` block. Example for a Rust
repo that also has TOML configs:
```
[*]
# ... (template content)
[*.toml]
indent_size = 2
```

## Detection
The CI script `scripts/check-editorconfig-template.sh` flags any repo
whose `.editorconfig` is the canonical 18-line pattern without a `# Source:` comment.

## Adoption sweep
As of 2026-06-11, 531 `.editorconfig` files in the org. Of those, the
majority are the canonical pattern (with slight per-repo variations).
V9-T3-3c is the follow-up wave that adopts this template.
