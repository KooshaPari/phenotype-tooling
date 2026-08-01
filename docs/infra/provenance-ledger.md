# Local Infrastructure Provenance Ledger

**Snapshot:** 2026-08-01  
**Scope:** `~/bin`, `~/.cursor`, Forge runtime state, and package-manager
resolution on the macOS development host. This is an inventory and decision
record; it is not a release manifest.

## Resolution and ownership

| Command | Resolved path | Observed version | Provenance / status |
|---|---|---:|---|
| `forge` | `~/.local/bin/forge` | 2.13.19 | Runtime install; canonical source is `CodeProjects/Phenotype/repos/forgecode`; version differs from local Cargo copy. |
| `forgecode` | `~/.local/bin/forgecode` | 2.10.1 | Runtime companion; source-backed by `repos/forgecode`; GitHub release assets exist. |
| `helioslite` | `~/.cargo/bin/helioslite` | 0.1.0-dev | Cargo path install from `repos/forgecode/crates/forge_main`; not a crates.io publication. |
| `elicitate` | `~/.local/bin/elicitate` | 0.9.0 | Source-backed by `repos/phenotype-tooling/crates/elicitate`. |
| `elicitate-mcp` | `~/.local/bin/elicitate-mcp` | 0.9.0 | Byte-identical companion in `~/.cargo/bin`; source-backed by `phenotype-tooling`. |
| `agileplus` | `~/bin/agileplus` | 0.2.1 | PATH winner is an ad-hoc binary; canonical source/package is `repos/AgilePlus` (`agileplus-cli`). Compare against `~/.cargo/bin/agileplus` before replacement. |
| `semgrep` | `/opt/homebrew/bin/semgrep` | 1.157.0 | Homebrew-managed, but Miniforge may shadow it in other shells. |
| `snyk` | `/opt/homebrew/bin/snyk` | not captured | npm-global installation under the Homebrew prefix. |
| `sentry-cli` | `/usr/local/bin/sentry-cli` | not captured | Resolved binary is not proven Homebrew-owned; verify before claiming package-manager custody. |
| `endorctl` | missing | — | Cursor cache references Endor sources, but no executable is installed. |

### Duplicate and unowned surfaces

- Forge has multiple local generations: `~/.local/bin` (2.13.19/2.10.1),
  `~/.cargo/bin` (2.10.0 path-installed binaries), and `~/.helioslite/bin`
  (2.10.0). Do not silently replace one with another.
- `~/bin` contains 35 regular files and eight symlinks; seven symlinks are
  broken (including `omniroute`, `pheno`, `pheno-llm`, `proccompose`, and
  `argis`). Eleven Mach-O files are ad-hoc/unsigned and several have no local
  source proof. `hermit -> hermit-stable` is the only known valid link.
- `~/bin/agileplus.real` is a stale 0.1.0 binary. `~/bin/agileplus` and the
  Cargo binary have different hashes despite sharing a 0.2.1 version.
- `~/.cursor` is primarily state/cache (~3 GB), not a source repository. Its
  custom Elicitate source is the `phenotype-tooling` checkout; other plugin
  caches are upstream mirrors or lack a local Git source.

## Package-manager and publication decisions

| Channel | Current evidence | Decision |
|---|---|---|
| Homebrew | No Forge/Helios/AgilePlus/Elicitate formula installed. | **Do not publish yet.** Add a formula only after a signed, checksum-pinned `KooshaPari/forgecode` release and stable artifact URLs are verified. |
| npm | Global tree contains vendor tooling (including Snyk); no Koosha Forge package surfaced. | **No publication.** Release workflow still targets upstream npm/Homebrew repositories and must be corrected first. |
| PyPI | No pipx-managed local tools; Forge is not a Python package. | **Not applicable / no publication.** |
| NuGet | Global .NET tool list is empty. | **Not applicable / no publication.** |
| Cargo | Forge local tools are path/git/workspace installs; `cargo package -p forge_main` fails because internal workspace crates are not on crates.io. | **Keep local/path installation.** Do not claim crates.io availability until the full workspace packaging contract passes. |

## Canonical source map

- Forge: `CodeProjects/Phenotype/repos/forgecode`, GitHub
  `KooshaPari/forgecode`. Current checkout is on a preservation branch and
  contains local work; preserve its branch and provenance.
- Elicitate: `CodeProjects/Phenotype/repos/phenotype-tooling`, crate
  `crates/elicitate`; GitHub `KooshaPari/phenotype-tooling`.
- AgilePlus: `CodeProjects/Phenotype/repos/AgilePlus`, package
  `agileplus-cli`.
- Cursor plugin caches: treat as runtime state unless a cache entry resolves to
  a separately owned repository; do not promote cache contents into releases.

## Safety and next gates

This ledger intentionally performs no deletion, relinking, cleanup, binary
replacement, package publication, or forced push. Before any promotion:

1. Record SHA-256, owner, build inputs, and smoke-test output for the candidate.
2. Repair stale Forge release references (notably `KooshaPari/heliosLite`) and
   validate the release workflow against `KooshaPari/forgecode`.
3. Reconcile PATH precedence so one intentional version wins per command.
4. Publish only a channel whose package metadata, signatures/checksums, and
   install smoke test all pass.
