#!/usr/bin/env python
"""
Patch script for Pydantic to work with Python 3.12.

This script directly patches the Python typing module's ForwardRef._evaluate method
to handle the missing recursive_guard parameter in Pydantic v1.
"""

import sys
import types
import typing
import inspect

def patch_forwardref():
    """
    Patch the ForwardRef._evaluate method to handle the missing recursive_guard parameter.
    """
    print(f"Python version: {sys.version}")
    
    # Only apply patches for Python 3.12+
    if sys.version_info < (3, 12):
        print("Python version is below 3.12, no patching needed")
        return
    
    # Check if ForwardRef exists in typing module
    if not hasattr(typing, "ForwardRef"):
        print("ForwardRef not found in typing module, no patching needed")
        return
    
    # Get the original _evaluate method
    original_evaluate = typing.ForwardRef._evaluate
    
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
        print(f"Using patched ForwardRef._evaluate with recursive_guard={recursive_guard}")
        # Call the original method without the recursive_guard parameter
        return original_evaluate(self, globalns, localns)
    
    # Apply the patch
    typing.ForwardRef._evaluate = patched_evaluate
    print("Successfully patched typing.ForwardRef._evaluate")

if __name__ == "__main__":
    patch_forwardref()
