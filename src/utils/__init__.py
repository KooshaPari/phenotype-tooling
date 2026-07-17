"""
Utility modules for the SWE agent.
"""

# Import the pydantic_compat module to apply patches
from .pydantic_compat import apply_pydantic_patches

# Apply Pydantic patches
apply_pydantic_patches()
