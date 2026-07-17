#!/usr/bin/env python
"""
Wrapper script to run the SWE Agent API server with Pydantic patches.

This script:
1. Applies the Pydantic patches for Python 3.12 compatibility
2. Runs the API server
"""

import sys
import os
import subprocess

def main():
    """
    Main function to run the patched API server.
    """
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the patch script
    patch_script = os.path.join(current_dir, "patch_pydantic.py")
    
    # Path to the API server script
    api_script = os.path.join(current_dir, "run_api.py")
    
    # Print information
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current directory: {current_dir}")
    print(f"Patch script: {patch_script}")
    print(f"API script: {api_script}")
    
    # Apply the patch
    print("\n=== Applying Pydantic patch ===")
    exec(open(patch_script).read())
    
    # Set environment variables
    os.environ["API_MODE"] = "true"
    os.environ["TUI_ENABLED"] = "false"
    
    # Run the API server
    print("\n=== Starting API server ===")
    
    # Import and run the API server
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,  # Disable reload to avoid issues with the patch
    )

if __name__ == "__main__":
    main()
