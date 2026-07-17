#!/usr/bin/env python
"""
Script to clean up PTY devices and processes.
This helps resolve the 'out of pty devices' error.
"""

import os
import signal
import subprocess
import sys
import time

def list_processes_using_pty():
    """List processes that are using PTY devices."""
    try:
        # Use lsof to find processes using /dev/pty* or /dev/tty*
        result = subprocess.run(
            ["lsof", "+c", "0", "-a", "-d", "0-255", "/dev/pty*", "/dev/tty*"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0 and not result.stdout:
            print("No processes found using PTY devices or lsof command failed.")
            return []
            
        # Parse the output to extract PIDs
        lines = result.stdout.strip().split('\n')
        if len(lines) <= 1:  # Only header or empty
            return []
            
        processes = []
        for line in lines[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 2:
                try:
                    pid = int(parts[1])
                    command = parts[0]
                    device = parts[3] if len(parts) > 3 else "unknown"
                    processes.append((pid, command, device))
                except (ValueError, IndexError):
                    continue
                    
        return processes
    except Exception as e:
        print(f"Error listing processes: {e}")
        return []

def kill_process(pid, command):
    """Attempt to kill a process by PID."""
    try:
        # First try SIGTERM
        os.kill(pid, signal.SIGTERM)
        print(f"Sent SIGTERM to process {pid} ({command})")
        
        # Wait a moment to see if it terminates
        time.sleep(0.5)
        
        # Check if process still exists
        try:
            os.kill(pid, 0)  # Signal 0 is used to check if process exists
            # Process still exists, try SIGKILL
            os.kill(pid, signal.SIGKILL)
            print(f"Sent SIGKILL to process {pid} ({command})")
        except OSError:
            # Process no longer exists
            print(f"Process {pid} ({command}) terminated successfully")
            return True
            
        return True
    except Exception as e:
        print(f"Error killing process {pid} ({command}): {e}")
        return False

def cleanup_pty_devices():
    """Clean up PTY devices by terminating processes using them."""
    print("Scanning for processes using PTY devices...")
    processes = list_processes_using_pty()
    
    if not processes:
        print("No processes found using PTY devices.")
        return
        
    print(f"Found {len(processes)} processes using PTY devices:")
    for pid, command, device in processes:
        print(f"  PID {pid}: {command} (using {device})")
        
    # Ask for confirmation before killing processes
    if input("Do you want to terminate these processes? (y/n): ").lower() != 'y':
        print("Cleanup aborted.")
        return
        
    # Kill processes
    killed_count = 0
    for pid, command, _ in processes:
        if kill_process(pid, command):
            killed_count += 1
            
    print(f"Terminated {killed_count} out of {len(processes)} processes.")
    
    # Check if we still have PTY issues
    try:
        # Try to open a PTY to see if we've resolved the issue
        import pty
        master, slave = pty.openpty()
        os.close(master)
        os.close(slave)
        print("Successfully opened a PTY device. The issue appears to be resolved.")
    except OSError as e:
        print(f"Still having PTY issues: {e}")
        print("You may need to restart your system to fully resolve this issue.")

if __name__ == "__main__":
    print("PTY Device Cleanup Utility")
    print("==========================")
    print("This utility will help clean up processes using PTY devices.")
    print("This can resolve the 'out of pty devices' error.")
    print()
    
    cleanup_pty_devices()
