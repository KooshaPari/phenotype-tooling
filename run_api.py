"""
Script to run the SWE Agent API server.
"""

# Apply Pydantic compatibility patches before any imports
import sys
import os
import atexit

# Add the current directory to the path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and apply Pydantic patches
from src.utils.pydantic_compat import apply_pydantic_patches

apply_pydantic_patches()

# Import PTY manager to handle PTY device allocation
from src.utils.pty_manager import cleanup_all_ptys, get_active_pty_count

# Register PTY cleanup on exit
atexit.register(cleanup_all_ptys)

# Print initial PTY status
print(f"Active PTY count at startup: {get_active_pty_count()}")

import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set API_MODE environment variable to disable TUI when running the API
os.environ["API_MODE"] = "true"
os.environ["TUI_ENABLED"] = "false"

# Run the API server
if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print("Starting SWE Agent API server...")

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8002")),  # Changed port to 8002 to avoid conflicts
        reload=True,
    )
