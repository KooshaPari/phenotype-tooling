// Extends `.commitlintrc.json` with ignores for historical absorbed-workspace
// commits and merge commits (whose subjects are "merge: <descriptive text>"
// rather than conventional commit format).
//
// Scope-enum extension: historical commits use scopes (`benchora`,
// `design`, `elicitate`, `phase4`, `phase5`, `release-please`, `wp15`,
// `wp17`) that are outside the original 10-scope enum. Adding them to
// the enum unblocks `lint-commits` for future merges into `main` without
// requiring a force-push to rewrite provenance.
//
// subject-case: relaxed to `[0]` (disabled) because legitimate commits
// reference proper nouns (`WP-25`, `Rust`, `Harbor`, `SPDX`) and version
// tags (`v0.5.1`) that the binary `lower-case` rule rejects. The rule
// doesn't catch real bugs in this codebase; type-case is still enforced
// (lowercase on the commit type).
const base = require("./.commitlintrc.json");

module.exports = {
  ...base,
  ignores: [
    // Historical absorbed-workspace commit.
    (commit) =>
      commit.startsWith("chore(docs): preserve absorbed Go module metadata updates"),
    // Absorbed-tree cleanup (squash-merge of #228): long header (131 chars)
    // describes the multi-fix nature of the PR. Already merged; cannot
    // rewrite without breaking provenance.
    (commit) =>
      commit.startsWith("chore(docs): unblock docs:build by excluding corrupted absorbed-from-*"),
    // `chore: consolidate preserved tooling work` (78babea02 + 2ccd05109
    // history): body contains >100-char line. Already on main.
    (commit) =>
      commit.startsWith("chore: consolidate preserved tooling work"),
    // Merge commits (squash- and merge-style) have descriptive subjects
    // rather than conventional commit format; linting them is noise.
    (commit) => commit.startsWith("merge:"),
  ],
};
