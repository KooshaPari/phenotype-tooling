# cliff.toml Adoption Guide

## TL;DR
Replace your `cliff.toml` with the canonical template at
[`templates/cliff.toml`](https://github.com/KooshaPari/phenotype-tooling/blob/main/templates/cliff.toml).
For 95%+ of repos, this is the entire change.

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
