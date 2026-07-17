"""
PTY Manager for handling PTY device allocation and cleanup.
This helps prevent 'out of pty devices' errors by properly managing PTY resources.
"""

import os
import signal
import subprocess
import time
import atexit
import threading
import weakref
from typing import Dict, List, Tuple, Set, Optional

class PTYManager:
    """
    Manages PTY devices to prevent resource exhaustion.
    Keeps track of allocated PTYs and ensures they're properly cleaned up.
    """
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PTYManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._active_ptys: Dict[int, Tuple[int, int, weakref.ref]] = {}  # pid -> (master_fd, slave_fd, obj_ref)
        self._cleanup_thread = None
        self._stop_event = threading.Event()
        
        # Register cleanup on exit
        atexit.register(self.cleanup_all)
        
        # Start monitoring thread
        self._start_monitor()
    
    def _start_monitor(self):
        """Start a background thread to monitor PTY usage."""
        self._cleanup_thread = threading.Thread(
            target=self._monitor_ptys,
            daemon=True,
            name="PTYMonitor"
        )
        self._cleanup_thread.start()
    
    def _monitor_ptys(self):
        """Monitor thread that periodically checks for orphaned PTYs."""
        while not self._stop_event.wait(30):  # Check every 30 seconds
            self.cleanup_orphaned()
    
    def register_pty(self, pid: int, master_fd: int, slave_fd: int, owner: object) -> None:
        """
        Register a new PTY allocation.
        
        Args:
            pid: Process ID using the PTY
            master_fd: Master file descriptor
            slave_fd: Slave file descriptor
            owner: Object that owns this PTY (will be weakly referenced)
        """
        with self._lock:
            self._active_ptys[pid] = (master_fd, slave_fd, weakref.ref(owner))
            print(f"PTY Manager: Registered PTY for PID {pid}")
    
    def unregister_pty(self, pid: int) -> None:
        """
        Unregister a PTY allocation.
        
        Args:
            pid: Process ID to unregister
        """
        with self._lock:
            if pid in self._active_ptys:
                del self._active_ptys[pid]
                print(f"PTY Manager: Unregistered PTY for PID {pid}")
    
    def cleanup_orphaned(self) -> int:
        """
        Clean up any orphaned PTY allocations.
        
        Returns:
            Number of PTYs cleaned up
        """
        to_cleanup = []
        
        with self._lock:
            for pid, (master_fd, slave_fd, obj_ref) in list(self._active_ptys.items()):
                # Check if the owner object is gone
                if obj_ref() is None:
                    to_cleanup.append(pid)
                    continue
                    
                # Check if the process is still running
                try:
                    os.kill(pid, 0)  # Signal 0 just checks if process exists
                except OSError:
                    # Process is gone
                    to_cleanup.append(pid)
        
        # Clean up the identified orphans
        for pid in to_cleanup:
            self.cleanup_pty(pid)
            
        return len(to_cleanup)
    
    def cleanup_pty(self, pid: int) -> bool:
        """
        Clean up a specific PTY allocation.
        
        Args:
            pid: Process ID to clean up
            
        Returns:
            True if cleanup was successful
        """
        with self._lock:
            if pid not in self._active_ptys:
                return False
                
            master_fd, slave_fd, _ = self._active_ptys[pid]
            
            # Try to close the file descriptors
            try:
                os.close(master_fd)
            except (OSError, IOError):
                pass
                
            try:
                os.close(slave_fd)
            except (OSError, IOError):
                pass
            
            # Try to terminate the process
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
                try:
                    os.kill(pid, 0)
                    # Process still exists, try SIGKILL
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    # Process is gone
                    pass
            except OSError:
                # Process is already gone
                pass
            
            # Remove from our tracking
            del self._active_ptys[pid]
            print(f"PTY Manager: Cleaned up PTY for PID {pid}")
            return True
    
    def cleanup_all(self) -> int:
        """
        Clean up all tracked PTY allocations.
        
        Returns:
            Number of PTYs cleaned up
        """
        with self._lock:
            pids = list(self._active_ptys.keys())
            
        count = 0
        for pid in pids:
            if self.cleanup_pty(pid):
                count += 1
                
        # Stop the monitor thread
        self._stop_event.set()
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(1.0)
            
        return count
    
    @property
    def active_pty_count(self) -> int:
        """Get the number of active PTYs being tracked."""
        with self._lock:
            return len(self._active_ptys)
    
    def get_active_ptys(self) -> List[Tuple[int, object]]:
        """
        Get a list of active PTYs and their owners.
        
        Returns:
            List of (pid, owner_object) tuples
        """
        with self._lock:
            result = []
            for pid, (_, _, obj_ref) in self._active_ptys.items():
                owner = obj_ref()
                if owner is not None:
                    result.append((pid, owner))
            return result

# Create a singleton instance
pty_manager = PTYManager()

# Monkey patch pty.fork to track PTY allocations
import pty as _original_pty

_original_fork = _original_pty.fork

def _patched_fork():
    """
    Patched version of pty.fork that registers with the PTY manager.
    """
    pid, fd = _original_fork()
    if pid > 0:  # Parent process
        # Get the calling object (usually a pexpect.spawn instance)
        import inspect
        frame = inspect.currentframe()
        try:
            # Look up the call stack to find the owner object
            while frame:
                if 'self' in frame.f_locals and hasattr(frame.f_locals['self'], 'pid'):
                    owner = frame.f_locals['self']
                    # Register with the manager
                    pty_manager.register_pty(pid, fd, -1, owner)
                    break
                frame = frame.f_back
        finally:
            del frame  # Avoid reference cycles
    
    return pid, fd

# Apply the monkey patch
_original_pty.fork = _patched_fork

def cleanup_all_ptys():
    """Clean up all tracked PTYs."""
    return pty_manager.cleanup_all()

def get_active_pty_count():
    """Get the number of active PTYs."""
    return pty_manager.active_pty_count
