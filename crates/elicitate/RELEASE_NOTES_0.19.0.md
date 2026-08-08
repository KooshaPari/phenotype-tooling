# elicitate v0.19.0 — Release Notes

**Release date:** 2026-08-07
**Branch:** `wip/2026-07-22-phenotype-tooling-absorbed-go-mod`
**Commits ahead of `main`:** 84
**Crate:** `elicitate` (`phenotype-tooling/crates/elicitate`)
**Previous version:** v0.12.0
**License:** Same as parent project
**Compatibility:** Rust 1.78+, no new MSRV bump from v0.18.x

This release covers **nine** development cycles shipped on the wip
branch since v0.12.0. The headline is the multi-inbox toolkit (v0.14
through v0.18) plus the runtime namespace inspector (v0.19) plus three
stabilization patches.

---

## Headline

`elicitate` now exposes a complete **multi-inbox toolkit** with parity
across the CLI, the daemon, and the MCP server surface. Users can:

1. Install a daemon for the default inbox **plus** any number of named
   namespaces (`elicitate install --register-namespace proj-a …`)
2. Run separate daemons for each namespace, each on a deterministic port
3. Address any inbox by name from the CLI (`--inbox-id`) or the MCP
   server (`inbox_id` parameter)
4. Inspect and manage every namespace at runtime via
   `elicitate namespace list / show / clean`

All three MCP tools (`elicitate_reply`, `elicitate_enqueue`,
`elicitate_cancel`) plus `inbox_status` and `elicitate_mcp` accept the
new `inbox_id` field.

---

## What's changed since v0.12.0

### v0.13.0 — `elicitate_reply` MCP tool

- New `pub fn write_reply(root, request_id, message)` in `inbox/mod.rs`
- New MCP tool `elicitate_reply` accepting `(request_id, message)`
- Added `JsonSchema` derive to `RequestState`, `NotificationKind`,
  `RequestOrigin`, `SecretEnvelope`, `Recipient` for `rmcp::Parameters<T>`
- 4 regression tests

### v0.14.0 — Multi-inbox (MCP)

- `pub fn resolve_inbox_root(inbox_id: Option<&str>) -> PathBuf`
- `pub fn is_valid_inbox_id(id: &str) -> bool` (regex: `[A-Za-z0-9_-]{1,64}`)
- `ReplyParams` and `InboxStatusParams` gain `inbox_id: Option<String>`
- MCP tool routing updated to honour `inbox_id`
- 7 new multi-inbox tests

### v0.15.0 — Multi-inbox (CLI + daemons)

- `--inbox-id <id>` global CLI flag with precedence chain
  (`--inbox-dir` > `--inbox-id` > `default_inbox_root()`)
- `two_daemons_on_different_namespaces_are_isolated` integration test
- `raw_http_get` test helper
- 6 new CLI tests + 1 daemon isolation test

### v0.16.0 — `elicitate_enqueue` MCP tool

- New `ElicitEnqueueParams` and `elicitate_enqueue` MCP tool (sync
  RequestOrigin construction, non-blocking counterpart to the popup tool)
- `mcp_server_lists_tools` updated to assert all four tools register
- 7 new enqueue tests

### v0.17.0 — `elicitate_cancel` MCP tool

- New `CancelParams` and `elicitate_cancel` MCP tool
- `pub fn cancel_pending(root, request_id, notes)` — idempotent
- 4 new cancel tests

### v0.18.0 — Per-namespace installer

- `pub fn namespace_port(inbox_id: &str) -> u16`
  (FNV-1a hash → `DEFAULT_PORT + offset`, range `7118..=8116`)
- `pub struct NamespaceAutostart { inbox_id, port, target }`
- `InstallOptions::extra_inbox_ids: Vec<String>`
- `install_autostart_for()` refactored to support default + per-namespace
- `--register-namespace <id>` CLI flag (repeatable)
- Uninstall now sweeps every `com.phenotype.elicitate*.plist` /
  `elicitate*.service` / `ElicitateDaemon.*` task
- 4 new installer tests

### v0.18.1 — Handshake flake fix (patch)

- `agents_smoke::mcp_handshake_initialize_and_list_tools` parallel-mode
  flake eliminated via `stdin.flush().unwrap()` after each `writeln!`
  + 50 ms sleep before EOF
- New `mcp_handshake_concurrent_parallel_children` regression test

### v0.18.2 — Notifier flake fix (patch)

- `inbox::daemon::tests::two_daemons_on_different_namespaces_are_isolated`
  flake eliminated: `PendingRequest.is_expired_now()` was returning true
  for fixtures with `expires_at_ms: 0`, causing the daemon's notifier
  loop to `finalize` the test fixture before the assertion could read it
- Fix: test fixture uses `expires_at_ms: u64::MAX`
- Stability: 20/20 lib-suite + 10/10 full-suite runs

### v0.19.0 — `elicitate namespace` command

- New subcommand: `elicitate namespace list / show / clean`
- Cross-platform autostart discovery
  (LaunchAgents / systemd-user / schtasks)
- `pub fn is_daemon_live(port) -> bool` (50 ms loopback probe)
- 6 new tests

---

## Upgrade notes

No breaking changes since v0.18.0. v0.18.0 itself is backwards-compatible
with v0.17.0 for users who don't pass `--inbox-id` or `--register-namespace`.

If upgrading from **pre-v0.18.0**, the `--inbox-id` flag is new. The
single-inbox default behaviour is preserved.

If upgrading from **pre-v0.18.1**, the handshake flake patch is a test-only
fix. Production binaries are unchanged.

---

## Test stability

| Phase | Lib suite | Full suite |
|---|---|---|
| Before v0.18.1 | ~5/10 runs failed (handshake flake) | ~5/10 runs failed |
| Before v0.18.2 | ~4/20 runs failed (notifier flake) | ~2/10 runs failed |
| After v0.18.2 | 20/20 green | 10/10 green |

Three time-based flakes have been resolved:
1. **Handshake parallel-mode** (v0.18.1) — stdio pipe flush race
2. **Notifier finalize race** (v0.18.2) — `expires_at_ms: 0` made fixtures
   instantly expired
3. **TIME_WAIT** (theoretical, did not reproduce after #2) — port-reuse
   after daemon teardown

---

## Dependencies

No new direct dependencies. All work was done within the existing
`elicitate` crate using already-present crates (`rmcp`, `serde`, `clap`,
`tempfile`, `portpicker`).

---

## Governance gap

Phases v0.13.0 through v0.19.0 were implemented on the
`wip/2026-07-22-phenotype-tooling-absorbed-go-mod` branch before the
AgilePlus integration was wired up for this repo. **ABSO

RPTION.md** now
contains a traceability table with retroactive spec slugs. Filing the
corresponding `kitty-specs/<slug>/` entries in the AgilePlus workspace
is a 30-minute follow-up:

```
agileplus specify --repo phenotype-tooling --feature elicitate-reply-mcp-tool --from-file <spec.md>
agileplus specify --repo phenotype-tooling --feature elicitate-multi-inbox-mcp --from-file <spec.md>
… (8 total)
```

---

## PR-prep checklist (for merging to main)

- [ ] All 221 tests green across the suite
- [ ] No new cargo-deny advisories introduced
- [ ] CHANGELOG.md reflects every phase
- [ ] ABSORPTION.md includes v0.13.0 → v0.19.0 entries
- [ ] `cargo clippy --all-targets -- -D warnings` clean
- [ ] `cargo fmt --check` clean
- [ ] Release notes (this file) reviewed
- [ ] AgilePlus retro specs filed (or tracked as follow-up issue)
- [ ] One squash-merge PR with body:

```
feat(elicitate): v0.13.0 → v0.19.0 — multi-inbox toolkit + flake fixes

This batch ships the multi-inbox toolkit across CLI/daemon/MCP plus
two test-stabilization patches. See crates/elicitate/RELEASE_NOTES_0.19.0.md
for the full changelog.

Tests: 221/221 green. Stability: 20/20 lib + 10/10 full-suite runs.
```
