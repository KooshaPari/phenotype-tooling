# PTY Device Troubleshooting

This document provides guidance on resolving the "out of pty devices" error that can occur when running the SWE Agent.

## Understanding the Issue

The error `OSError: out of pty devices` occurs when the system has exhausted all available pseudo-terminal (PTY) devices. This typically happens when:

1. Many terminal sessions are created and not properly closed
2. Processes that use PTY devices (like `pexpect.spawn`) are not properly terminated
3. The system has been running for a long time without a restart

## Quick Fix

If you encounter this error, you can use the provided cleanup utility to free up PTY resources:

```bash
python run_cleanup.py
```

This utility will:
1. Scan for processes using PTY devices
2. List these processes and ask for confirmation
3. Terminate the processes to free up PTY resources

## Prevention Measures

The SWE Agent now includes a PTY Manager that helps prevent this issue by:

1. Tracking all PTY allocations
2. Automatically cleaning up orphaned PTYs
3. Ensuring PTYs are properly closed when the application exits

## Manual Cleanup Steps

If the cleanup utility doesn't resolve the issue, you can try these manual steps:

### 1. Find processes using PTY devices

```bash
lsof +c 0 -a -d 0-255 /dev/pty* /dev/tty*
```

### 2. Terminate these processes

```bash
kill -TERM <PID>
```

If a process doesn't terminate, use:

```bash
kill -KILL <PID>
```

### 3. Last Resort: Restart your system

If all else fails, restarting your system will reset all PTY devices.

## Technical Details

### PTY Device Limits

macOS has a limited number of PTY devices available (typically 128). When all are in use, the system returns the "out of pty devices" error.

### How the PTY Manager Works

The PTY Manager in `src/utils/pty_manager.py` works by:

1. Monkey patching `pty.fork()` to track all PTY allocations
2. Using weak references to detect when owner objects are garbage collected
3. Periodically checking for orphaned PTYs
4. Automatically cleaning up resources when the application exits

### Debugging PTY Usage

To check the current PTY usage in your application, you can use:

```python
from src.utils.pty_manager import get_active_pty_count
print(f"Active PTY count: {get_active_pty_count()}")
```

## Contact

If you continue to experience PTY-related issues after trying these solutions, please report the issue with details about your environment and the steps you've taken.
