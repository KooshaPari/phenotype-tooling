"""
Configuration utilities for loading and managing application settings.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# Determine the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
CONFIG_DIR = PROJECT_ROOT / "config"

# Look for config.json in the new directory first, then the root directory, then fall back to the config directory
NEW_CONFIG_PATH = PROJECT_ROOT / "new" / "config.json"
ROOT_CONFIG_PATH = PROJECT_ROOT / "config.json"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "config.json"
CONFIG_FILE_PATH = os.environ.get(
    "CONFIG_FILE_PATH",
    str(
        NEW_CONFIG_PATH
        if NEW_CONFIG_PATH.exists()
        else (ROOT_CONFIG_PATH if ROOT_CONFIG_PATH.exists() else DEFAULT_CONFIG_PATH)
    ),
)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from the specified JSON file.

    Args:
        config_path: Path to the config file. If None, uses the default config.json.

    Returns:
        Dict containing the configuration.
    """
    if config_path is None:
        config_path = CONFIG_FILE_PATH

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Warning: Config file not found at {config_path}. Using empty config.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from config file at {config_path}.")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred while loading config: {e}")
        return {}


def get_mcp_tools_config() -> List[Dict[str, Any]]:
    """
    Get the MCP tools configuration.

    Returns:
        List of MCP tool configurations.
    """
    config = load_config()
    # Check for both formats - old format with mcp_tools array and new format with mcpServers
    if "mcp_tools" in config:
        return config.get("mcp_tools", [])
    return []


def get_mcp_servers_config() -> Dict[str, Dict[str, Any]]:
    """
    Get the MCP servers configuration.

    Returns:
        Dictionary of MCP server configurations.
    """
    config = load_config()
    # Check for both formats - old format with mcp_servers array and new format with mcpServers
    if "mcp_servers" in config:
        # Convert old format to new format
        servers = {}
        for server in config.get("mcp_servers", []):
            if server.get("disabled", False):
                continue
            name = server.get("name", "default")
            servers[name] = {
                "command": server.get("command"),
                "args": server.get("args", []),
                "transport": server.get("transport", "stdio"),
                "autoApprove": server.get("auto_approve", []),
                "timeout": server.get("timeout", 60),
                "env": server.get("env", {}),
            }
        return servers
    elif "mcpServers" in config:
        # Use the new format directly
        servers = {}
        for name, server_config in config.get("mcpServers", {}).items():
            if server_config.get("disabled", False):
                continue

            # Create a new config with the correct transport key
            new_config = server_config.copy()

            # If transportType exists, use it for transport and remove transportType
            if "transportType" in new_config:
                new_config["transport"] = new_config.pop("transportType")
            # If neither transport nor transportType exists, default to stdio
            elif "transport" not in new_config:
                new_config["transport"] = "stdio"

            servers[name] = new_config

        return servers
    return {}


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an environment variable.

    Args:
        name: Name of the environment variable.
        default: Default value if the environment variable is not set.

    Returns:
        Value of the environment variable or default.
    """
    return os.environ.get(name, default)
