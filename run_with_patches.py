#!/usr/bin/env python
"""
Combined script to apply all patches and run the API server.

This script:
1. Applies patches to both typing and pydantic modules
2. Runs the API server
"""

import sys
import os
import importlib.util
import types

def apply_patches():
    """Apply all patches for Python 3.12 compatibility."""
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Only apply patches for Python 3.12+
    if sys.version_info < (3, 12):
        print("Python version is below 3.12, no patching needed")
        return
    
    # Patch the typing module
    print("\n=== Patching typing module ===")
    try:
        import typing
        
        # Check if ForwardRef exists in typing module
        if not hasattr(typing, "ForwardRef"):
            print("ForwardRef not found in typing module, no patching needed")
        else:
            # Get the original _evaluate method
            original_evaluate = typing.ForwardRef._evaluate
            
            # Create a patched version that handles the missing recursive_guard parameter
            def patched_evaluate(self, globalns, localns, recursive_guard=None):
                """
                Patched version of ForwardRef._evaluate that handles the missing recursive_guard parameter.
                """
                # Call the original method without the recursive_guard parameter
                return original_evaluate(self, globalns, localns)
            
            # Apply the patch
            typing.ForwardRef._evaluate = patched_evaluate
            print("Successfully patched typing.ForwardRef._evaluate")
    except Exception as e:
        print(f"Error patching typing module: {e}")
    
    # Try to patch pydantic directly
    print("\n=== Patching pydantic module ===")
    try:
        # Try to find the pydantic module
        spec = importlib.util.find_spec("pydantic")
        if spec is None:
            print("Pydantic module not found")
        else:
            # Load the module
            pydantic = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pydantic)
            
            # Check if v1 exists
            if not hasattr(pydantic, "v1"):
                print("Pydantic v1 not found")
            else:
                # Try to patch the typing module
                try:
                    # Load the typing module
                    typing_spec = importlib.util.find_spec("pydantic.v1.typing")
                    if typing_spec is None:
                        print("Pydantic v1 typing module not found")
                    else:
                        # Load the module
                        pydantic_typing = importlib.util.module_from_spec(typing_spec)
                        typing_spec.loader.exec_module(pydantic_typing)
                        
                        # Check if ForwardRef exists
                        if not hasattr(pydantic_typing, "ForwardRef"):
                            print("ForwardRef not found in pydantic.v1.typing")
                        else:
                            # Get the original _evaluate method
                            original_evaluate = pydantic_typing.ForwardRef._evaluate
                            
                            # Create a patched version that handles the missing recursive_guard parameter
                            def patched_evaluate(self, globalns, localns, recursive_guard=None):
                                """
                                Patched version of ForwardRef._evaluate that handles the missing recursive_guard parameter.
                                """
                                # Call the original method without the recursive_guard parameter
                                return original_evaluate(self, globalns, localns)
                            
                            # Apply the patch
                            pydantic_typing.ForwardRef._evaluate = patched_evaluate
                            print("Successfully patched pydantic.v1.typing.ForwardRef._evaluate")
                except Exception as e:
                    print(f"Error patching pydantic.v1.typing: {e}")
    except Exception as e:
        print(f"Error patching pydantic module: {e}")
    
    print("\n=== Patches applied ===")

def run_api():
    """Run the API server."""
    print("\n=== Starting API server ===")
    
    # Set environment variables
    os.environ["API_MODE"] = "true"
    os.environ["TUI_ENABLED"] = "false"
    
    # Import and run the API server
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,  # Disable reload to avoid issues with the patch
    )

if __name__ == "__main__":
    # Apply patches
    apply_patches()
    
    # Run the API server
    run_api()
