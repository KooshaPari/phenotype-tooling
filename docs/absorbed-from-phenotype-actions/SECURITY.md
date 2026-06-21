# Security policy

If you discover a security issue in phenotype-actions, please email
`security@phenotype.dev` rather than opening a public issue. PGP key:
`0xDEADBEEF`.

## Supported versions

| Version | Supported |
| ------- | --------- |
| v0.1.x  | yes       |

## Pinned third-party actions

All third-party actions used in this repo are pinned by commit SHA
(not by tag). To update a pin, open a PR that updates the SHA in
`.github/workflows/*.yml` and the lookup table in
`actions/pin-sha/action.yml`. Dependabot is configured to open these
PRs automatically.

## Trust model

Consumers of `phenotype-actions` trust:

1. The maintainers of this repo not to introduce a malicious workflow.
2. The maintainers of upstream third-party actions not to rewrite a
   pinned tag to point to a new commit.

Pin to a specific tag of this repo (`@v0.1.0`) rather than `@main` to
get reproducible builds.
