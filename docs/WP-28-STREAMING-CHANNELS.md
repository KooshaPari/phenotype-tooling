# WP-28: Streaming Release Channels

## Goal

Per-stream release channels (`stable` / `beta` / `nightly`) so consumers of the 3 release streams introduced by WP-25 can opt into different release cadences. `pt` exposes a `pt upgrade channel` subcommand that reads the current channel from `~/.pt/config.toml` and pulls the latest release matching it.

## Channel taxonomy

| Channel | Source | Cadence | Stability | Use case |
|---|---|---|---|---|
| `stable` | Tagged releases on `main` | Per WP merged | High | Production consumers |
| `beta` | PRs with `channel: beta` label | Weekly | Medium | Pre-production validation |
| `nightly` | Latest commit on `main` | Daily | Low | Continuous integration against main |

Each channel maps to a different `releases/v{channel}/latest` JSON manifest published by the WP-28 workflow.

## Architecture

```
release-please PR merge (per stream)
  -> tag push (e.g. cli-stream-v0.3.0)
    -> publish-channel.yml workflow
       -> write releases/stable/cli-stream-latest.json
       -> write releases/v0.3.0/cli-stream-manifest.json
  -> on: schedule (weekly for beta, daily for nightly)
    -> publish-channel.yml workflow
       -> rebuild channel manifests from current main
```

`pt upgrade channel` reads:
- `~/.pt/config.toml` (channel, current_version)
- `<channel-manifest-url>` (returns latest version per stream)

And pulls each stream to the latest version matching the channel.

## Per-channel manifest schema

```json
{
  "channel": "stable",
  "generated_at": "2026-07-04T03:00:00Z",
  "streams": {
    "core-stream": {
      "version": "0.3.0",
      "tag": "core-stream-v0.3.0",
      "manifest_url": "https://github.com/.../releases/download/core-stream-v0.3.0/manifest.json",
      "released_at": "2026-07-04T02:42:00Z"
    },
    "cli-stream": { "version": "0.2.0", "tag": "cli-stream-v0.2.0", ... },
    "ops-stream":  { "version": "0.2.0", "tag": "ops-stream-v0.2.0",  ... }
  }
}
```

## Acceptance criteria

1. `publish-channel.yml` runs on every release tag push, weekly for beta, daily for nightly
2. `pt upgrade channel stable` upgrades all 3 streams to the latest stable
3. `pt upgrade channel beta` upgrades to latest beta
4. `pt upgrade channel nightly` upgrades to latest commit on main
5. Channel manifests are atomic writes (write to .tmp + rename) so partial reads are never served
6. Manifest URLs are immutable (tag-based, never overwrite)
7. Old channel manifests retained for 1 year (auditability)

## Files

| File | Purpose |
|---|---|
| `.github/workflows/publish-channel.yml` | Publishes per-channel manifests on tag push + schedule |
| `crates/phenotype-cli/src/cmd_upgrade.rs` | `pt upgrade channel <name>` subcommand |
| `crates/phenotype-cli/src/lib.rs` | Wire `Upgrade(Args)` into `enum Command` |
| `crates/phenotype-cli/src/config.rs` | `~/.pt/config.toml` parser/writer |
| `scripts/channel_manifest.py` | Builder for the per-channel manifest |
| `docs/WP-28-STREAMING-CHANNELS.md` | This file |
