#!/usr/bin/env python3
"""
Terminal Launcher - Utility for launching terminal windows for agents.

This module provides functions for launching terminal windows to view and interact
with agent processes.
"""

import os
import sys
import subprocess
import platform
import logging
from typing import Dict, Optional, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("terminal-launcher")

# Dictionary to track terminal processes for each agent
terminal_processes: Dict[str, subprocess.Popen] = {}

def get_terminal_command(title: str, command: str) -> List[str]:
    """Get the appropriate terminal launch command based on the platform.
    
    Args:
        title: The title for the terminal window
        command: The command to run in the terminal
        
    Returns:
        The terminal launch command as a list of arguments
    """
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # Use AppleScript to launch Terminal.app with a custom title and command
        return [
            "osascript", 
            "-e", 
            f'tell application "Terminal" to do script "{command}"',
            "-e",
            f'tell application "Terminal" to set custom title of front window to "{title}"',
            "-e",
            'tell application "Terminal" to activate'
        ]
    elif system == "Linux":
        # Try to detect the available terminal emulator
        if os.path.exists("/usr/bin/gnome-terminal"):
            return ["gnome-terminal", "--title", title, "--", "bash", "-c", f"{command}; exec bash"]
        elif os.path.exists("/usr/bin/xterm"):
            return ["xterm", "-title", title, "-e", f"{command}; exec bash"]
        elif os.path.exists("/usr/bin/konsole"):
            return ["konsole", "--title", title, "-e", f"{command}; exec bash"]
        else:
            # Default to xterm if available
            return ["xterm", "-title", title, "-e", f"{command}; exec bash"]
    elif system == "Windows":
        # For Windows, use start cmd with a title
        return ["cmd", "/c", "start", f"cmd /k title {title} & {command}"]
    else:
        # Default case - just return the command
        logger.warning(f"Unsupported platform: {system}, using default command")
        return ["bash", "-c", command]

def launch_agent_terminal(agent_id: str, agent_name: str, command: Optional[str] = None) -> bool:
    """Launch a terminal window for an agent.
    
    Args:
        agent_id: The agent ID
        agent_name: The agent name (for display purposes)
        command: Optional command to run in the terminal
        
    Returns:
        True if the terminal was launched successfully, False otherwise
    """
    try:
        # Close existing terminal if one exists for this agent
        close_agent_terminal(agent_id)
        
        # Create a title for the terminal
        title = f"Agent: {agent_name} ({agent_id})"
        
        # If no command is provided, use a default command that shows agent info
        if not command:
            command = f"echo 'Agent: {agent_name}\\nID: {agent_id}\\n\\nUse this terminal to interact with the agent.\\n'; exec bash"
        
        # Get the terminal launch command
        terminal_cmd = get_terminal_command(title, command)
        
        logger.info(f"Launching terminal for agent {agent_id} with command: {terminal_cmd}")
        
        # Launch the terminal
        process = subprocess.Popen(
            terminal_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Store the process
        terminal_processes[agent_id] = process
        
        return True
    except Exception as e:
        logger.error(f"Error launching terminal for agent {agent_id}: {e}")
        return False

def close_agent_terminal(agent_id: str) -> bool:
    """Close the terminal window for an agent.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        True if the terminal was closed successfully, False otherwise
    """
    if agent_id in terminal_processes:
        try:
            process = terminal_processes[agent_id]
            
            # Check if the process is still running
            if process.poll() is None:
                # Process is still running, terminate it
                process.terminate()
                try:
                    # Wait for the process to terminate
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # If it doesn't terminate within the timeout, kill it
                    process.kill()
            
            # Remove the process from the dictionary
            del terminal_processes[agent_id]
            
            logger.info(f"Closed terminal for agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Error closing terminal for agent {agent_id}: {e}")
            return False
    
    # No terminal process found for this agent
    return False

def get_agent_terminal_status(agent_id: str) -> Dict[str, Any]:
    """Get the status of the terminal for an agent.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        A dictionary with the terminal status
    """
    if agent_id in terminal_processes:
        process = terminal_processes[agent_id]
        
        # Check if the process is still running
        is_running = process.poll() is None
        
        return {
            "has_terminal": True,
            "is_running": is_running,
            "pid": process.pid if is_running else None
        }
    
    return {
        "has_terminal": False,
        "is_running": False,
        "pid": None
    }

def get_all_terminal_statuses() -> Dict[str, Dict[str, Any]]:
    """Get the status of all agent terminals.
    
    Returns:
        A dictionary mapping agent IDs to terminal status dictionaries
    """
    statuses = {}
    
    for agent_id, process in terminal_processes.items():
        # Check if the process is still running
        is_running = process.poll() is None
        
        statuses[agent_id] = {
            "has_terminal": True,
            "is_running": is_running,
            "pid": process.pid if is_running else None
        }
    
    return statuses

# Test function
if __name__ == "__main__":
    # Test launching a terminal
    agent_id = "test-agent-123"
    agent_name = "Test Agent"
    
    print(f"Launching terminal for {agent_name}...")
    success = launch_agent_terminal(agent_id, agent_name)
    
    if success:
        print("Terminal launched successfully!")
        
        # Wait for a moment
        import time
        time.sleep(5)
        
        # Get terminal status
        status = get_agent_terminal_status(agent_id)
        print(f"Terminal status: {status}")
        
        # Close the terminal
        print("Closing terminal...")
        close_agent_terminal(agent_id)
        
        # Get terminal status again
        status = get_agent_terminal_status(agent_id)
        print(f"Terminal status after closing: {status}")
    else:
        print("Failed to launch terminal.")
