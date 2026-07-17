#!/usr/bin/env python
"""
Direct patch script for Pydantic v1 to work with Python 3.12.

This script directly modifies the Pydantic v1 typing module to fix the ForwardRef._evaluate method.
"""

import sys
import os
import inspect
import importlib
import types

def patch_pydantic_direct():
    """
    Directly patch the Pydantic v1 typing module.
    """
    print(f"Python version: {sys.version}")
    
    # Only apply patches for Python 3.12+
    if sys.version_info < (3, 12):
        print("Python version is below 3.12, no patching needed")
        return
    
    try:
        # Try to import pydantic v1 typing module
        import pydantic.v1.typing as pydantic_typing
        
        # Check if ForwardRef exists
        if not hasattr(pydantic_typing, "ForwardRef"):
            print("ForwardRef not found in pydantic.v1.typing, no patching needed")
            return
        
        # Get the original _evaluate method
        original_evaluate = pydantic_typing.ForwardRef._evaluate
        
        # Check if the method already has the recursive_guard parameter
        sig = inspect.signature(original_evaluate)
        if "recursive_guard" in sig.parameters:
            print("ForwardRef._evaluate already has recursive_guard parameter, no patching needed")
            return
        
        # Create a patched version that handles the missing recursive_guard parameter
        def patched_evaluate(self, globalns, localns, recursive_guard=None):
            """
            Patched version of ForwardRef._evaluate that handles the missing recursive_guard parameter.
            """
            print(f"Using patched Pydantic ForwardRef._evaluate with recursive_guard={recursive_guard}")
            # Call the original method without the recursive_guard parameter
            return original_evaluate(self, globalns, localns)
        
        # Apply the patch
        pydantic_typing.ForwardRef._evaluate = patched_evaluate
        print("Successfully patched pydantic.v1.typing.ForwardRef._evaluate")
        
    except ImportError:
        print("Could not import pydantic.v1.typing, skipping patch")
    
    try:
        # Also try to patch the typing module directly
        import typing
        
        # Check if ForwardRef exists in typing module
        if not hasattr(typing, "ForwardRef"):
            print("ForwardRef not found in typing module, no patching needed")
            return
        
        # Get the original _evaluate method
        original_evaluate = typing.ForwardRef._evaluate
        
        # Check if the method already has the recursive_guard parameter
        sig = inspect.signature(original_evaluate)
        if "recursive_guard" in sig.parameters:
            print("typing.ForwardRef._evaluate already has recursive_guard parameter, no patching needed")
            return
        
        # Create a patched version that handles the missing recursive_guard parameter
        def patched_evaluate(self, globalns, localns, recursive_guard=None):
            """
            Patched version of ForwardRef._evaluate that handles the missing recursive_guard parameter.
            """
            print(f"Using patched typing.ForwardRef._evaluate with recursive_guard={recursive_guard}")
            # Call the original method without the recursive_guard parameter
            return original_evaluate(self, globalns, localns)
        
        # Apply the patch
        typing.ForwardRef._evaluate = patched_evaluate
        print("Successfully patched typing.ForwardRef._evaluate")
        
    except Exception as e:
        print(f"Error patching typing module: {e}")

if __name__ == "__main__":
    patch_pydantic_direct()
