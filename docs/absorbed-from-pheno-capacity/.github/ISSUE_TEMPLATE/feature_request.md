---
name: Feature request
about: Propose a new capacity-math formula, kind, or anchor
title: "[feat] "
labels: ["enhancement", "triage"]
assignees: []
---

## Summary

<!-- One sentence: what do you want to add? -->

## Motivation

<!-- What real-world model or workload motivates this? Cite a paper / vendor doc if possible. -->

## Proposed API

```rust
// Sketch of the public function / struct / variant.
```

## Backwards compatibility

- [ ] Additive only (new function, new variant, new field with `Default`)
- [ ] Touches existing signature (breaking — needs ADR + CHANGELOG entry)

## ADR / spec impact

- ADR: <!-- ADR-XXX -->
- Spec: <!-- docs/SPEC.md §X -->
- Methodology doc: <!-- docs/methodology.md §X -->

## Acceptance criteria

- [ ] Public API added with doc-test
- [ ] Unit tests cover at least one real-world anchor
- [ ] `cargo test --no-default-features` still passes (`no_std` constraint)
- [ ] CHANGELOG.md updated
