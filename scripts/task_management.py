#!/usr/bin/env python3
"""
Task Management Module - Tools for managing tasks and work breakdown structures.

This module provides tools for creating, updating, and managing tasks and
work breakdown structures for agent swarms.
"""

import os
import sys
import json
import uuid
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("task-management")

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastmcp import FastMCP, Context
    logger.info("Successfully imported FastMCP")
except ImportError:
    logger.error("Failed to import FastMCP. Please install it with 'pip install fastmcp'")
    sys.exit(1)

# Import agent registry
try:
    from agent_registry import get_registry
    logger.info("Successfully imported agent registry")
except ImportError:
    logger.error("Failed to import agent registry")
    sys.exit(1)

# Task status enum
class TaskStatus(str, Enum):
    PLANNED = "planned"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

# Task priority enum
class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Initialize agent registry
registry = get_registry()

# In-memory storage for tasks
tasks_storage = {}

# In-memory storage for work breakdown structures
wbs_storage = {}

# Create the FastMCP server
mcp = FastMCP(
    name="Task Management",
    description="Tools for managing tasks and work breakdown structures"
)

@mcp.tool(
    annotations={
        "title": "Create Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def create_task(
    title: str,
    description: str,
    creator_id: str,
    assignee_id: Optional[str] = None,
    parent_task_id: Optional[str] = None,
    wbs_id: Optional[str] = None,
    priority: str = TaskPriority.MEDIUM,
    estimated_hours: Optional[float] = None,
    deadline: Optional[str] = None,
    dependencies: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new task.
    
    Args:
        title: The task title
        description: The task description
        creator_id: The ID of the agent creating the task
        assignee_id: Optional ID of the agent assigned to the task
        parent_task_id: Optional ID of the parent task
        wbs_id: Optional ID of the work breakdown structure
        priority: Task priority (low, medium, high, critical)
        estimated_hours: Optional estimated hours to complete
        deadline: Optional deadline for the task (ISO format)
        dependencies: Optional list of task IDs this task depends on
        tags: Optional list of tags for the task
        metadata: Optional additional metadata
        
    Returns:
        The created task
    """
    logger.info(f"Creating task: {title}")
    
    try:
        # Check if creator exists
        creator = registry.get_agent(creator_id)
        if not creator:
            return {"error": f"Creator agent with ID '{creator_id}' not found"}
        
        # Check if assignee exists if provided
        if assignee_id:
            assignee = registry.get_agent(assignee_id)
            if not assignee:
                return {"error": f"Assignee agent with ID '{assignee_id}' not found"}
        
        # Check if parent task exists if provided
        if parent_task_id and parent_task_id not in tasks_storage:
            return {"error": f"Parent task with ID '{parent_task_id}' not found"}
        
        # Check if WBS exists if provided
        if wbs_id and wbs_id not in wbs_storage:
            return {"error": f"Work breakdown structure with ID '{wbs_id}' not found"}
        
        # Generate task ID
        task_id = f"task-{uuid.uuid4().hex}"
        
        # Create task
        timestamp = datetime.now(timezone.utc).isoformat()
        
        task = {
            "task_id": task_id,
            "title": title,
            "description": description,
            "creator_id": creator_id,
            "assignee_id": assignee_id,
            "parent_task_id": parent_task_id,
            "wbs_id": wbs_id,
            "status": TaskStatus.PLANNED if not assignee_id else TaskStatus.ASSIGNED,
            "priority": priority,
            "estimated_hours": estimated_hours,
            "deadline": deadline,
            "dependencies": dependencies or [],
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": timestamp,
            "updated_at": timestamp,
            "completed_at": None,
            "subtasks": []
        }
        
        # Store task
        tasks_storage[task_id] = task
        
        # Add to parent task's subtasks if applicable
        if parent_task_id:
            tasks_storage[parent_task_id]["subtasks"].append(task_id)
        
        # Add to WBS if applicable
        if wbs_id:
            if "tasks" not in wbs_storage[wbs_id]:
                wbs_storage[wbs_id]["tasks"] = []
            
            wbs_storage[wbs_id]["tasks"].append(task_id)
            wbs_storage[wbs_id]["updated_at"] = timestamp
        
        # Update assignee status if assigned
        if assignee_id:
            registry.update_agent(assignee_id, {"status": "busy"})
        
        return {
            "task": task,
            "message": "Task created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return {"error": str(e), "status": "error"}

@mcp.tool(
    annotations={
        "title": "Get Task",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
async def get_task(
    task_id: str,
    include_subtasks: bool = False
) -> Dict[str, Any]:
    """Get a task by ID.
    
    Args:
        task_id: The task ID
        include_subtasks: Whether to include subtask details
        
    Returns:
        The task information
    """
    logger.info(f"Getting task: {task_id}")
    
    try:
        # Check if task exists
        if task_id not in tasks_storage:
            return {"error": f"Task with ID '{task_id}' not found"}
        
        task = tasks_storage[task_id]
        
        # Include subtask details if requested
        if include_subtasks and task["subtasks"]:
            subtasks = []
            for subtask_id in task["subtasks"]:
                if subtask_id in tasks_storage:
                    subtasks.append(tasks_storage[subtask_id])
            
            task_copy = task.copy()
            task_copy["subtasks"] = subtasks
            return {"task": task_copy}
        
        return {"task": task}
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        return {"error": str(e), "status": "error"}

@mcp.tool(
    annotations={
        "title": "Update Task",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    assignee_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    estimated_hours: Optional[float] = None,
    deadline: Optional[str] = None,
    dependencies: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Update a task.
    
    Args:
        task_id: The task ID
        title: Optional new title
        description: Optional new description
        assignee_id: Optional new assignee ID
        status: Optional new status
        priority: Optional new priority
        estimated_hours: Optional new estimated hours
        deadline: Optional new deadline
        dependencies: Optional new dependencies
        tags: Optional new tags
        metadata: Optional new metadata
        
    Returns:
        The updated task
    """
    logger.info(f"Updating task: {task_id}")
    
    try:
        # Check if task exists
        if task_id not in tasks_storage:
            return {"error": f"Task with ID '{task_id}' not found"}
        
        task = tasks_storage[task_id]
        
        # Check if assignee exists if provided
        if assignee_id is not None:
            if assignee_id:
                assignee = registry.get_agent(assignee_id)
                if not assignee:
                    return {"error": f"Assignee agent with ID '{assignee_id}' not found"}
        
        # Update task fields
        if title is not None:
            task["title"] = title
        
        if description is not None:
            task["description"] = description
        
        if assignee_id is not None:
            old_assignee_id = task["assignee_id"]
            task["assignee_id"] = assignee_id
            
            # Update status if assigning for the first time
            if not old_assignee_id and assignee_id:
                task["status"] = TaskStatus.ASSIGNED
            
            # Update agent statuses
            if assignee_id:
                registry.update_agent(assignee_id, {"status": "busy"})
            
            if old_assignee_id and old_assignee_id != assignee_id:
                registry.update_agent(old_assignee_id, {"status": "active"})
        
        if status is not None:
            task["status"] = status
            
            # Update completed_at if status is completed
            if status == TaskStatus.COMPLETED and not task["completed_at"]:
                task["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            # Update assignee status if task is completed or failed
            if status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and task["assignee_id"]:
                registry.update_agent(task["assignee_id"], {"status": "active"})
        
        if priority is not None:
            task["priority"] = priority
        
        if estimated_hours is not None:
            task["estimated_hours"] = estimated_hours
        
        if deadline is not None:
            task["deadline"] = deadline
        
        if dependencies is not None:
            task["dependencies"] = dependencies
        
        if tags is not None:
            task["tags"] = tags
        
        if metadata is not None:
            task["metadata"] = {**task["metadata"], **metadata}
        
        # Update timestamp
        task["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Update WBS if applicable
        if task["wbs_id"] and task["wbs_id"] in wbs_storage:
            wbs_storage[task["wbs_id"]]["updated_at"] = task["updated_at"]
        
        return {
            "task": task,
            "message": "Task updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return {"error": str(e), "status": "error"}

@mcp.tool(
    annotations={
        "title": "Create Work Breakdown Structure",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def create_wbs(
    name: str,
    description: str,
    creator_id: str,
    project_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new work breakdown structure.
    
    Args:
        name: The WBS name
        description: The WBS description
        creator_id: The ID of the agent creating the WBS
        project_id: Optional project ID
        metadata: Optional additional metadata
        
    Returns:
        The created WBS
    """
    logger.info(f"Creating WBS: {name}")
    
    try:
        # Check if creator exists
        creator = registry.get_agent(creator_id)
        if not creator:
            return {"error": f"Creator agent with ID '{creator_id}' not found"}
        
        # Generate WBS ID
        wbs_id = f"wbs-{uuid.uuid4().hex}"
        
        # Create WBS
        timestamp = datetime.now(timezone.utc).isoformat()
        
        wbs = {
            "wbs_id": wbs_id,
            "name": name,
            "description": description,
            "creator_id": creator_id,
            "project_id": project_id,
            "tasks": [],
            "metadata": metadata or {},
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        # Store WBS
        wbs_storage[wbs_id] = wbs
        
        return {
            "wbs": wbs,
            "message": "Work breakdown structure created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating WBS: {e}")
        return {"error": str(e), "status": "error"}

@mcp.tool(
    annotations={
        "title": "Get Work Breakdown Structure",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
async def get_wbs(
    wbs_id: str,
    include_tasks: bool = False
) -> Dict[str, Any]:
    """Get a work breakdown structure by ID.
    
    Args:
        wbs_id: The WBS ID
        include_tasks: Whether to include task details
        
    Returns:
        The WBS information
    """
    logger.info(f"Getting WBS: {wbs_id}")
    
    try:
        # Check if WBS exists
        if wbs_id not in wbs_storage:
            return {"error": f"Work breakdown structure with ID '{wbs_id}' not found"}
        
        wbs = wbs_storage[wbs_id]
        
        # Include task details if requested
        if include_tasks and wbs["tasks"]:
            tasks = []
            for task_id in wbs["tasks"]:
                if task_id in tasks_storage:
                    tasks.append(tasks_storage[task_id])
            
            wbs_copy = wbs.copy()
            wbs_copy["tasks"] = tasks
            return {"wbs": wbs_copy}
        
        return {"wbs": wbs}
    except Exception as e:
        logger.error(f"Error getting WBS: {e}")
        return {"error": str(e), "status": "error"}

@mcp.tool(
    annotations={
        "title": "List Tasks",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
async def list_tasks(
    wbs_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """List tasks with optional filtering.
    
    Args:
        wbs_id: Optional WBS ID to filter by
        assignee_id: Optional assignee ID to filter by
        status: Optional status to filter by
        priority: Optional priority to filter by
        tags: Optional tags to filter by
        limit: Maximum number of tasks to return
        offset: Number of tasks to skip
        
    Returns:
        List of tasks
    """
    logger.info("Listing tasks")
    
    try:
        # Get all tasks
        all_tasks = list(tasks_storage.values())
        
        # Apply filters
        filtered_tasks = all_tasks
        
        if wbs_id:
            filtered_tasks = [t for t in filtered_tasks if t["wbs_id"] == wbs_id]
        
        if assignee_id:
            filtered_tasks = [t for t in filtered_tasks if t["assignee_id"] == assignee_id]
        
        if status:
            filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
        
        if priority:
            filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority]
        
        if tags:
            filtered_tasks = [t for t in filtered_tasks if any(tag in t["tags"] for tag in tags)]
        
        # Sort by updated_at (newest first)
        filtered_tasks = sorted(filtered_tasks, key=lambda t: t["updated_at"], reverse=True)
        
        # Apply pagination
        paginated_tasks = filtered_tasks[offset:offset + limit]
        
        return {
            "tasks": paginated_tasks,
            "total": len(filtered_tasks),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        return {"error": str(e), "status": "error"}

# Main entry point
if __name__ == "__main__":
    # Run the server
    logger.info("Starting task management server")
    mcp.run(transport="stdio")
