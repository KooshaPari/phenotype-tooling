# Research Report: Simulation & Sandbox (Deterministic Replay)

> **WORK_STREAM ID**: research-simulation-replay
> **Status**: ✅ Research Phase Complete
> **Date**: 2026-02-19

## Executive Summary

The research for Simulation & Sandbox (WP-4007) is complete. The system enables deterministic replay of past agent decisions by retrieving context from Supermemory L3 and artifacts from L4. This capability is critical for debugging, audit, and autonomous learning refinement.

## Key Findings

1. **Deterministic Strategy**: Requires sandboxed execution, mocked external APIs, deterministic random seeds, and state snapshots to ensure "same input -> same output".
2. **Architecture**: Uses `SimulationReplay` manager to reconstruct the decision environment from L3 context and L4 artifacts.
3. **Verification**: Matches output hashes of replayed decisions against original `MAIFArtifact` records.
4. **Use Cases**: Debugging (why a decision was made), testing (logic verification), and learning (refining models based on past success/failure).

## Implementation Status

- **Replay Logic**: Python-based `SimulationReplay` design complete.
- **Environment Reconstruction**: Patterns for state snapshotting and mocking defined.
- **Sandbox**: Basic sandbox implementation exists in `ux/compositor.py`.

## Next Steps

1. Implement the `SimulationReplay` engine in `src/thegent/ux/replay.py`.
2. Enhance state snapshotting capabilities in the `ExecutionEngine`.
3. Integrate replay tools into the developer CLI (`thegent debug replay`).

## Reference

Detailed research available in [SESSION_RESEARCH_FRAGMENTS_EXPANDED.md](./SESSION_RESEARCH_FRAGMENTS_EXPANDED.md).
