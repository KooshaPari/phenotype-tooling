# CODEOWNERS Adoption Guide

## TL;DR
Replace your `.github/CODEOWNERS` with a copy of
[`templates/CODEOWNERS`](https://github.com/KooshaPari/phenotype-tooling/blob/main/templates/CODEOWNERS).
For 90%+ of repos, this is the entire change.

## When you need more
Add path-specific rules BELOW the `* @KooshaPari` line. Example:
```
* @KooshaPari
/.github/workflows/ @platform-team
/docs/ @docs-team
/SECURITY.md @security-team
```

## Detection
The CI script `scripts/check-codeowners-template.sh` flags any repo
whose `.github/CODEOWNERS` is exactly `* @KooshaPari` without
referencing this template via a `# Source:` comment.

## Adoption sweep
As of 2026-06-11, 42 of 627 CODEOWNERS files in the org are exactly
`* @KooshaPari`. These are the V13-T3-2c adoption targets.
