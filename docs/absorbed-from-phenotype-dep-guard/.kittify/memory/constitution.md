# Template Program Constitution

## Principles

1. Layer-first architecture over copy-paste scaffolds.
2. One concern per template layer (commons, language, domain).
3. Non-destructive reconcile by default (`smart`).
4. Explicit version pinning for every consumed layer.
5. Fail loudly on contract drift and unresolved conflicts.

## Delivery Rules

1. No hidden overwrites.
2. Every layer change requires manifest version bump.
3. Every release must pass manifest + reconcile smoke checks.
4. Domain layers must depend only on commons + exactly one primary language layer.

## Quality Gates

1. Contract schema validity.
2. Reconcile rules validity.
3. Deterministic dry-run diff output.
4. Upgrade and rollback notes updated.
