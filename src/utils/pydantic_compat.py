"""
Compatibility layer for Pydantic to handle version differences.
This module provides monkey patches for Pydantic to work with Python 3.12.
"""

import sys
import inspect


def apply_pydantic_patches():
    """
    Apply monkey patches to make Pydantic work with Python 3.12.
    This function patches the ForwardRef._evaluate method to handle the missing recursive_guard parameter.
    """
    try:
        # Only apply patches for Python 3.12+
        if sys.version_info < (3, 12):
            return

        # Check if we're using Pydantic v1
        import pydantic

        if not hasattr(pydantic, "v1"):
            return

        # Import the typing module from Pydantic v1
        from pydantic.v1 import typing as pydantic_typing

        # Check if ForwardRef exists and needs patching
        if not hasattr(pydantic_typing, "ForwardRef"):
            return

        # Get the original _evaluate method
        original_evaluate = pydantic_typing.ForwardRef._evaluate

        # Create a patched version that handles the missing recursive_guard parameter
        def patched_evaluate(self, globalns, localns, *args, **kwargs):
            """
            Patched version of ForwardRef._evaluate that handles the missing recursive_guard parameter.
            """
            # Check the signature of the original method
            sig = inspect.signature(original_evaluate)
            params = list(sig.parameters.keys())

            # Handle different signatures
            if "recursive_guard" in params:
                # New signature with recursive_guard
                if "recursive_guard" in kwargs:
                    recursive_guard = kwargs["recursive_guard"]
                elif len(args) >= 1:
                    recursive_guard = args[0]
                else:
                    recursive_guard = set()

                # Call with the recursive_guard parameter as keyword argument
                return original_evaluate(
                    self, globalns, localns, recursive_guard=recursive_guard
                )
            else:
                # Old signature without recursive_guard
                return original_evaluate(self, globalns, localns)

        # Apply the patch
        pydantic_typing.ForwardRef._evaluate = patched_evaluate

        print("Applied Pydantic compatibility patches for Python 3.12")
    except Exception as e:
        print(f"Error applying Pydantic patches: {e}")


# Apply patches when the module is imported
apply_pydantic_patches()
