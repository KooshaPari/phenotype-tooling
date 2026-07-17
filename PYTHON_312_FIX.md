# Python 3.12 Compatibility Fix

This document provides solutions for running the SWE Agent with Python 3.12, which has compatibility issues with Pydantic v1.

## The Issue

Python 3.12 changed the signature of the `ForwardRef._evaluate` method to require a `recursive_guard` parameter. Pydantic v1 (used by LangChain and other dependencies) uses an older version of this method without the parameter, causing a `TypeError` when evaluating forward references:

```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

## Solution Options

### Option 1: Run with Patches (Recommended)

Use the `run_with_patches.py` script which applies patches to fix the compatibility issue:

```bash
python run_with_patches.py
```

This script:
1. Patches both the Python typing module and Pydantic v1 typing module
2. Runs the API server with the patches applied
3. Disables auto-reload to ensure the patches remain in effect

### Option 2: Downgrade Python

Use the `downgrade_python.sh` script to downgrade to Python 3.11:

```bash
chmod +x downgrade_python.sh
./downgrade_python.sh
```

This script:
1. Uses pyenv to install Python 3.11.7 if not already installed
2. Sets the local Python version to 3.11.7
3. Runs the API server with Python 3.11.7

### Option 3: Manual Patching

If you need to apply the patches manually:

```python
# Apply this patch before importing any modules that use Pydantic
import typing

# Get the original _evaluate method
original_evaluate = typing.ForwardRef._evaluate

# Create a patched version
def patched_evaluate(self, globalns, localns, recursive_guard=None):
    # Call the original method without the recursive_guard parameter
    return original_evaluate(self, globalns, localns)

# Apply the patch
typing.ForwardRef._evaluate = patched_evaluate
```

## Detailed Explanation

The error occurs because:
1. Python 3.12 changed the signature of the `ForwardRef._evaluate` method to require a `recursive_guard` parameter
2. Pydantic v1 was using an older version of this method without the parameter
3. This caused a `TypeError` when Pydantic tried to evaluate forward references

Our solution patches the method to handle both the old and new signatures, ensuring compatibility with Python 3.12.

## Long-term Solution

The long-term solution is to upgrade to Pydantic v2, which is fully compatible with Python 3.12. However, this requires updating all dependencies that rely on Pydantic v1, which may not be feasible in the short term.
