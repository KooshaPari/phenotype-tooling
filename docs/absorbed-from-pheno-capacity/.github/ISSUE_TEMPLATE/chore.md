---
name: Chore / governance
about: CODEOWNERS, templates, CI, justfile, docs housekeeping
title: "[chore] "
labels: ["chore", "governance"]
assignees: []
---

## Summary

<!-- One sentence: what governance artifact are you changing? -->

## Files touched

<!-- List the files (CODEOWNERS, .github/workflows/*.yml, justfile, docs/*.md, etc.). -->

## Risk

- [ ] None — pure documentation / template change
- [ ] Low — CI workflow change (test in a fork first)
- [ ] Medium — CODEOWNERS change (review by @KooshaPari required)

## Verification

- [ ] `cargo check` still passes (no source change)
- [ ] `git ls-files .github` reflects intended layout
