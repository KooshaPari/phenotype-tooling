# cliff.toml Adoption Guide

## TL;DR
Replace your `cliff.toml` with the canonical template at
[`templates/cliff.toml`](https://github.com/KooshaPari/phenotype-tooling/blob/main/templates/cliff.toml).
For 95%+ of repos, this is the entire change.

## v2 — Breaking changes

`templates/cliff.toml` is now at **v2** (2026-06-11). The only behavioural
change is that commits with a breaking-change marker (`!` suffix on a
conventional-commit type, e.g. `feat!: remove legacy API`) are now
highlighted in the rendered changelog with a `⚠️ **BREAKING**` suffix:

```markdown
### Features
- *(api)* Remove legacy v1 endpoints ⚠️ **BREAKING**
- Add experimental support for batch jobs

### Bug Fixes
- Fix off-by-one in retry counter
```

This is opt-out: a commit is considered breaking when git-cliff reports
`commit.breaking == true` (the standard `!` suffix or a `BREAKING CHANGE:`
footer). No change to commit messages is required to keep working — the
suffix only renders for breaking commits.

### v1 detection

`scripts/check-cliff-template.sh` detects v1 adopters and emits a
different warning so CI surfaces the upgrade. v1 is functionally
identical to v2 except for the breaking-change suffix. Adopted v1 repos
(`# Source:` comment present) are flagged for upgrade but otherwise work
fine; non-adopted v1 repos that already match the canonical pattern are
flagged for both adoption and upgrade.

## When you need more
Add per-section rules BELOW the standard `[changelog]` block. Example for a
repo with custom commit scopes:
```toml
[changelog]
# ... (template content)

# Custom: highlight breaking changes
body = """
{% for group, commits in commits | group_by(attribute="group") %}
    ### {{ group | upper_first }}
    {% if group == "Breaking" %}⚠️{% endif %}
    {% for commit in commits %}- ...{% endfor %}
{% endfor %}
"""
```

## Detection
The CI script `scripts/check-cliff-template.sh` flags any repo whose
`cliff.toml` matches the canonical pattern without a `# Source:` comment.

## Adoption sweep
As of 2026-06-11, 232 `cliff.toml` files in the org (100 mainline). The vast
majority share the standard pattern. V9-T3-4c is the follow-up wave.
