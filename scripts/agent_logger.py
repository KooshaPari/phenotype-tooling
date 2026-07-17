#!/usr/bin/env python3
"""
Agent Logger - Utility for managing agent logs and log viewers.

This module provides functions for setting up logging for agents and
launching log viewer terminals to monitor agent output in real-time.
"""

import os
import sys
import subprocess
import platform
import logging
import time
from pathlib import Path
from typing import Dict, Optional, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("agent-logger")

# Dictionary to track log viewer processes for each agent
log_viewer_processes: Dict[str, subprocess.Popen] = {}

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def get_agent_log_path(agent_id: str) -> str:
    """Get the log file path for an agent.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        The path to the agent's log file
    """
    return str(LOGS_DIR / f"{agent_id}.log")

def setup_agent_logging(agent_id: str, agent_name: str) -> str:
    """Set up logging for an agent.
    
    Args:
        agent_id: The agent ID
        agent_name: The agent name
        
    Returns:
        The path to the agent's log file
    """
    log_path = get_agent_log_path(agent_id)
    
    # Create the log file with a header
    with open(log_path, 'w') as f:
        f.write(f"=== Agent Log: {agent_name} ({agent_id}) ===\n")
        f.write(f"=== Started at: {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
    
    logger.info(f"Set up logging for agent {agent_id} at {log_path}")
    return log_path

def get_log_viewer_command(title: str, log_path: str) -> List[str]:
    """Get the appropriate log viewer command based on the platform.
    
    Args:
        title: The title for the terminal window
        log_path: The path to the log file to view
        
    Returns:
        The log viewer command as a list of arguments
    """
    system = platform.system()
    
    # The command to view logs (tail -f or equivalent)
    if system in ["Darwin", "Linux"]:
        view_cmd = f"tail -f '{log_path}'"
    else:  # Windows
        view_cmd = f"powershell -command \"Get-Content '{log_path}' -Wait\""
    
    if system == "Darwin":  # macOS
        # Use AppleScript to launch Terminal.app with a custom title and command
        return [
            "osascript", 
            "-e", 
            f'tell application "Terminal" to do script "{view_cmd}"',
            "-e",
            f'tell application "Terminal" to set custom title of front window to "{title}"',
            "-e",
            'tell application "Terminal" to activate'
        ]
    elif system == "Linux":
        # Try to detect the available terminal emulator
        if os.path.exists("/usr/bin/gnome-terminal"):
            return ["gnome-terminal", "--title", title, "--", "bash", "-c", f"{view_cmd}"]
        elif os.path.exists("/usr/bin/xterm"):
            return ["xterm", "-title", title, "-e", view_cmd]
        elif os.path.exists("/usr/bin/konsole"):
            return ["konsole", "--title", title, "-e", view_cmd]
        else:
            # Default to xterm if available
            return ["xterm", "-title", title, "-e", view_cmd]
    elif system == "Windows":
        # For Windows, use start cmd with a title
        return ["cmd", "/c", "start", f"cmd /k title {title} & {view_cmd}"]
    else:
        # Default case - just return the command
        logger.warning(f"Unsupported platform: {system}, using default command")
        return ["bash", "-c", view_cmd]

def launch_log_viewer(agent_id: str, agent_name: str) -> bool:
    """Launch a log viewer terminal for an agent.
    
    Args:
        agent_id: The agent ID
        agent_name: The agent name
        
    Returns:
        True if the log viewer was launched successfully, False otherwise
    """
    try:
        # Close existing log viewer if one exists for this agent
        close_log_viewer(agent_id)
        
        # Get the log file path
        log_path = get_agent_log_path(agent_id)
        
        # Create a title for the terminal
        title = f"Agent Log: {agent_name} ({agent_id})"
        
        # Get the log viewer command
        viewer_cmd = get_log_viewer_command(title, log_path)
        
        logger.info(f"Launching log viewer for agent {agent_id} with command: {viewer_cmd}")
        
        # Launch the log viewer
        process = subprocess.Popen(
            viewer_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Store the process
        log_viewer_processes[agent_id] = process
        
        return True
    except Exception as e:
        logger.error(f"Error launching log viewer for agent {agent_id}: {e}")
        return False

def close_log_viewer(agent_id: str) -> bool:
    """Close the log viewer terminal for an agent.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        True if the log viewer was closed successfully, False otherwise
    """
    if agent_id in log_viewer_processes:
        try:
            process = log_viewer_processes[agent_id]
            
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
            del log_viewer_processes[agent_id]
            
            logger.info(f"Closed log viewer for agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Error closing log viewer for agent {agent_id}: {e}")
            return False
    
    # No log viewer process found for this agent
    return False

def log_to_agent(agent_id: str, message: str, level: str = "INFO") -> bool:
    """Log a message to an agent's log file.
    
    Args:
        agent_id: The agent ID
        message: The message to log
        level: The log level (INFO, WARNING, ERROR, etc.)
        
    Returns:
        True if the message was logged successfully, False otherwise
    """
    try:
        log_path = get_agent_log_path(agent_id)
        
        # Format the log message
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"{timestamp} - {level} - {message}\n"
        
        # Append to the log file
        with open(log_path, 'a') as f:
            f.write(formatted_message)
        
        return True
    except Exception as e:
        logger.error(f"Error logging to agent {agent_id}: {e}")
        return False

def get_log_viewer_status(agent_id: str) -> Dict[str, Any]:
    """Get the status of the log viewer for an agent.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        A dictionary with the log viewer status
    """
    if agent_id in log_viewer_processes:
        process = log_viewer_processes[agent_id]
        
        # Check if the process is still running
        is_running = process.poll() is None
        
        return {
            "has_log_viewer": True,
            "is_running": is_running,
            "pid": process.pid if is_running else None,
            "log_path": get_agent_log_path(agent_id)
        }
    
    return {
        "has_log_viewer": False,
        "is_running": False,
        "pid": None,
        "log_path": get_agent_log_path(agent_id) if os.path.exists(get_agent_log_path(agent_id)) else None
    }

# Test function
if __name__ == "__main__":
    # Test setting up logging and launching a log viewer
    agent_id = "test-agent-123"
    agent_name = "Test Agent"
    
    print(f"Setting up logging for {agent_name}...")
    log_path = setup_agent_logging(agent_id, agent_name)
    print(f"Log path: {log_path}")
    
    print(f"Launching log viewer for {agent_name}...")
    success = launch_log_viewer(agent_id, agent_name)
    
    if success:
        print("Log viewer launched successfully!")
        
        # Log some test messages
        for i in range(5):
            print(f"Logging test message {i+1}...")
            log_to_agent(agent_id, f"Test message {i+1}")
            time.sleep(1)
        
        # Log a warning
        log_to_agent(agent_id, "This is a warning message", "WARNING")
        
        # Log an error
        log_to_agent(agent_id, "This is an error message", "ERROR")
        
        # Wait for a moment to see the logs
        time.sleep(5)
        
        # Get log viewer status
        status = get_log_viewer_status(agent_id)
        print(f"Log viewer status: {status}")
        
        # Close the log viewer
        print("Closing log viewer...")
        close_log_viewer(agent_id)
        
        # Get log viewer status again
        status = get_log_viewer_status(agent_id)
        print(f"Log viewer status after closing: {status}")
    else:
        print("Failed to launch log viewer.")
