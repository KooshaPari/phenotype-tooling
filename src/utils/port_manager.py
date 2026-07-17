"""
Port Manager Utility

This module provides utilities for finding available ports for agent processes.
"""

import socket
from typing import Set

# Keep track of allocated ports to avoid conflicts
_allocated_ports: Set[int] = set()

def find_available_port(start_port: int = 8006, max_attempts: int = 100) -> int:
    """
    Find an available port starting from start_port.
    
    Args:
        start_port: The starting port number to check.
        max_attempts: Maximum number of ports to try.
        
    Returns:
        An available port number.
        
    Raises:
        RuntimeError: If no available port is found.
    """
    for port in range(start_port, start_port + max_attempts):
        # Skip if we've already allocated this port
        if port in _allocated_ports:
            continue
            
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                # Mark this port as allocated
                _allocated_ports.add(port)
                return port
        except OSError:
            continue
    
    raise RuntimeError(
        f"No available port found in range {start_port}-{start_port + max_attempts}"
    )

def release_port(port: int) -> None:
    """
    Release a previously allocated port.
    
    Args:
        port: The port number to release.
    """
    _allocated_ports.discard(port)

def is_port_available(port: int) -> bool:
    """
    Check if a port is available.
    
    Args:
        port: The port number to check.
        
    Returns:
        True if the port is available, False otherwise.
    """
    if port in _allocated_ports:
        return False
        
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", port))
            return True
    except OSError:
        return False

def get_allocated_ports() -> Set[int]:
    """
    Get the set of currently allocated ports.
    
    Returns:
        A set of allocated port numbers.
    """
    return _allocated_ports.copy()
