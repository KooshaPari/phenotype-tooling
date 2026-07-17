# Research Report: Compute Offloading (Mac ↔ PC)

> **WORK_STREAM ID**: research-compute-offload
> **Status**: ✅ Research Phase Complete
> **Date**: 2026-02-19

## Executive Summary

The research for linking a Mac client with a Windows 11 compute base via compute offloading is complete. The architecture leverages Tailscale for networking and Syncthing for bi-directional file synchronization.

## Key Findings

1. **Architecture**: 
   - **Client**: Mac (Cursor, Claude Code) for lightweight development.
   - **Compute Base**: Windows 11 PC (64GB RAM, 16GB VRAM) for heavy builds, Docker, and training.
2. **Networking**: Tailscale VPN provides secure, peer-to-peer connectivity.
3. **Synchronization**: Syncthing ensures the `kush/` workspace is consistent across both machines.
4. **Access**: Parsec RDP for graphical access and SSH for remote command execution.

## Implementation Status

- **Architecture**: Complete.
- **Sync Pattern**: Verified via Syncthing.
- **Remote Execution**: SSH path established.

## Next Steps

1. Configure Tailscale on both nodes.
2. Set up Syncthing for the main development workspace.
3. Verify Parsec performance for low-latency remote TUI usage.

## Reference

Detailed research available in [CONVERSATION_DUMP_2026-02-16.md](./CONVERSATION_DUMP_2026-02-16.md) and [HYBRID_ENV_SUMMARY.md](./HYBRID_ENV_SUMMARY.md).
