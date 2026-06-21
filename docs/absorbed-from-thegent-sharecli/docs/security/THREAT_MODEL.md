# Threat Model

> **Source of truth:** thegent-sharecli (Hexagonal Python CLI: command deduplication, task queue, smart merge, multi-agent coordination)

## Scope

Hexagonal (Ports & Adapters) Python CLI that deduplicates commands, serializes them through a shared task queue, and performs smart merges across multiple agent-driven projects on the same workstation. It watches local files (`watchfiles`), validates every boundary with `pydantic` v2, and exposes operations via `typer`. Adversary is any process (including a sibling agent) that can write to the shared dedup store, drop a file inside a watched project, or invoke the CLI's own `thegent-sharecli` entrypoint.

## Assets

1. Command dedup keys/hashes and the in-process lock map (`InMemoryLockAdapter`) that gate concurrent execution.
2. The task queue state — pending, in-flight, completed task descriptors — that coordinates multi-agent progress.
3. Smart-merge inputs and results, which transit across project boundaries and may carry proprietary source content.
4. Watched project file trees, whose mutation is the de facto signal that kicks off dedup/queue work.
5. `pydantic` contract models that define the trust boundary between adapters and the core.
6. The CLI invocation surface itself — every `typer` subcommand is an attacker-controllable entry point.

## STRIDE Threats

- **Spoofing:** A malicious project fabricates a dedup key that collides with a legitimate agent's key, causing the legit agent's work to be silently shadowed. A second process impersonates the orchestrator on the watch channel and emits spurious "task complete" events.
- **Tampering:** A compromised dependency (or a sibling agent that shares the filesystem) writes into the dedup store or task queue mid-flight, reordering or dropping work. Tampering with a watched file forces an unintended merge; the smart-merge step is the highest-blast-radius mutation.
- **Repudiation:** Lock acquisition/release and task submission events have no signed audit trail — when a claim goes missing, no agent can be provably blamed. `InMemoryLockAdapter` is per-process, so a crash erases the only contemporaneous evidence.
- **Information Disclosure:** Dedup hashes leak command topology across projects; a project that observes another project's hashes learns what that project is running. Smart-merge error paths may surface diffs or file contents from a higher-trust project into a lower-trust one.
- **Denial of Service:** A burst of spurious lock claims starves legitimate ones; an aggressive watcher on one project floods the orchestrator and starves siblings. A pathological smart-merge (huge diff set) exhausts memory and freezes the queue.
- **Elevation of Privilege:** A low-trust project, by virtue of being on the same machine, shares the orchestrator's UID and can invoke any `typer` subcommand — including ones intended for higher-trust projects. A malicious `pydantic` model loaded from a watched dir could escape its adapter and reach the core.

## Residual Risk & Revision Cadence

The dominant residual risks are: (a) no authentication between adapters, so any local process is implicitly trusted; (b) `InMemoryLockAdapter` provides no persistence and no cross-process coordination, so a multi-agent setup that *thinks* it has shared locks does not; (c) smart-merge is a write primitive with no rollback audit. Mitigations to schedule: signed/per-project lock keys, persistent durable adapter, an append-only event log for repudiation resistance, project-scoping for `typer` subcommands, and resource caps on merge operations. This model is **reviewed quarterly** and **immediately** on any change to: the adapter port set, the dedup hash algorithm, the smart-merge backend, or the addition of a new `typer` subcommand.
