// Preserve one historical absorbed-workspace commit without weakening lint
// for current contributions or requiring a force-push to rewrite provenance.
const base = require("./.commitlintrc.json");

module.exports = {
  ...base,
  ignores: [
    (message) =>
      message.startsWith("chore(docs): preserve absorbed Go module metadata updates"),
  ],
};
