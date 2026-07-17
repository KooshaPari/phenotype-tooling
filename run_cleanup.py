#!/usr/bin/env python
"""
Script to run the PTY cleanup utility.
This helps resolve the 'out of pty devices' error.
"""

import os
import sys
import subprocess

def main():
    """Run the PTY cleanup utility."""
    print("Running PTY Cleanup Utility")
    print("==========================")
    
    # Get the path to the cleanup script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cleanup_script = os.path.join(script_dir, "cleanup_pty.py")
    
    # Check if the script exists
    if not os.path.exists(cleanup_script):
        print(f"Error: Cleanup script not found at {cleanup_script}")
        return 1
    
    # Run the cleanup script
    try:
        result = subprocess.run(
            [sys.executable, cleanup_script],
            check=True
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running cleanup script: {e}")
        return e.returncode
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
