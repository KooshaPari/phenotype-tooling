#!/usr/bin/env python3
"""
Agent Communication Module - Tools for agent-to-agent communication.

This module provides tools for agents to communicate with each other,
including sending and receiving messages, and task delegation.
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
logger = logging.getLogger("agent-communication")

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

# Message types
class MessageType(str, Enum):
    TEXT = "text"
    TASK = "task"
    RESULT = "result"
    STATUS = "status"
    ERROR = "error"
    SYSTEM = "system"

# Initialize agent registry
registry = get_registry()

# In-memory storage for message queues
message_queues = {}

# In-memory storage for conversation history
conversation_history = {}

# Create the FastMCP server
mcp = FastMCP(
    name="Agent Communication",
    description="Tools for agent-to-agent communication"
)

@mcp.tool(
    annotations={
        "title": "Send Message To Agent",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def send_message_to_agent(
    sender_id: str,
    recipient_id: str,
    content: str,
    message_type: str = MessageType.TEXT,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Send a message from one agent to another.
    
    Args:
        sender_id: The ID of the sender agent
        recipient_id: The ID of the recipient agent
        content: The message content
        message_type: The type of message (text, task, result, status, error, system)
        metadata: Optional metadata for the message
        
    Returns:
        The sent message information
    """
    logger.info(f"Sending message from {sender_id} to {recipient_id}")
    
    try:
        # Check if sender exists
        sender = registry.get_agent(sender_id)
        if not sender:
            return {"error": f"Sender agent with ID '{sender_id}' not found"}
        
        # Check if recipient exists
        recipient = registry.get_agent(recipient_id)
        if not recipient:
            return {"error": f"Recipient agent with ID '{recipient_id}' not found"}
        
        # Create message
        message_id = f"msg-{uuid.uuid4().hex}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        message = {
            "message_id": message_id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "content": content,
            "type": message_type,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "status": "delivered"
        }
        
        # Add to recipient's message queue
        if recipient_id not in message_queues:
            message_queues[recipient_id] = []
        
        message_queues[recipient_id].append(message)
        
        # Add to conversation history
        if sender_id not in conversation_history:
            conversation_history[sender_id] = []
        if recipient_id not in conversation_history:
            conversation_history[recipient_id] = []
        
        conversation_history[sender_id].append(message)
        conversation_history[recipient_id].append(message)
        
        # Update agent's last activity
        registry.update_agent(sender_id, {"last_activity": timestamp})
        
        return {
            "message": message,
            "status": "delivered",
            "timestamp": timestamp
        }
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {"error": str(e), "status": "error"}

@mcp.tool(
    annotations={
        "title": "Get Agent Messages",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
async def get_agent_messages(
    agent_id: str,
    limit: int = 10,
    offset: int = 0,
    message_type: Optional[str] = None,
    sender_id: Optional[str] = None,
    unread_only: bool = False
) -> Dict[str, Any]:
    """Get messages for an agent.
    
    Args:
        agent_id: The agent ID
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        message_type: Optional filter by message type
        sender_id: Optional filter by sender ID
        unread_only: Whether to return only unread messages
        
    Returns:
        List of messages
    """
    logger.info(f"Getting messages for agent: {agent_id}")
    
    try:
        # Check if agent exists
        agent = registry.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent with ID '{agent_id}' not found"}
        
        # Get messages from queue
        if agent_id not in message_queues:
            message_queues[agent_id] = []
        
        messages = message_queues[agent_id]
        
        # Apply filters
        if message_type:
            messages = [m for m in messages if m["type"] == message_type]
        
        if sender_id:
            messages = [m for m in messages if m["sender_id"] == sender_id]
        
        if unread_only:
            messages = [m for m in messages if m.get("status") != "read"]
        
        # Sort by timestamp (newest first)
        messages = sorted(messages, key=lambda m: m["timestamp"], reverse=True)
        
        # Apply pagination
        messages = messages[offset:offset + limit]
        
        # Mark messages as read
        for message in messages:
            message["status"] = "read"
        
        return {
            "messages": messages,
            "total": len(message_queues[agent_id]),
            "filtered": len(messages)
        }
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return {"error": str(e), "status": "error"}

@mcp.tool(
    annotations={
        "title": "Get Conversation History",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
async def get_conversation_history(
    agent_id: str,
    other_agent_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    include_system_messages: bool = False
) -> Dict[str, Any]:
    """Get conversation history for an agent.
    
    Args:
        agent_id: The agent ID
        other_agent_id: Optional other agent ID to filter conversation
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        include_system_messages: Whether to include system messages
        
    Returns:
        List of messages in the conversation
    """
    logger.info(f"Getting conversation history for agent: {agent_id}")
    
    try:
        # Check if agent exists
        agent = registry.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent with ID '{agent_id}' not found"}
        
        # Get conversation history
        if agent_id not in conversation_history:
            conversation_history[agent_id] = []
        
        messages = conversation_history[agent_id]
        
        # Apply filters
        if other_agent_id:
            messages = [
                m for m in messages 
                if (m["sender_id"] == other_agent_id and m["recipient_id"] == agent_id) or
                   (m["sender_id"] == agent_id and m["recipient_id"] == other_agent_id)
            ]
        
        if not include_system_messages:
            messages = [m for m in messages if m["type"] != MessageType.SYSTEM]
        
        # Sort by timestamp (newest first)
        messages = sorted(messages, key=lambda m: m["timestamp"], reverse=True)
        
        # Apply pagination
        messages = messages[offset:offset + limit]
        
        return {
            "messages": messages,
            "total": len(conversation_history[agent_id]),
            "filtered": len(messages)
        }
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return {"error": str(e), "status": "error"}

@mcp.tool(
    annotations={
        "title": "Assign Task To Agent",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def assign_task_to_agent(
    sender_id: str,
    recipient_id: str,
    task: Dict[str, Any],
    priority: str = "medium",
    deadline: Optional[str] = None
) -> Dict[str, Any]:
    """Assign a task to an agent.
    
    Args:
        sender_id: The ID of the sender agent
        recipient_id: The ID of the recipient agent
        task: The task details (must include at least 'title' and 'description')
        priority: Task priority (low, medium, high)
        deadline: Optional deadline for the task (ISO format)
        
    Returns:
        The task assignment information
    """
    logger.info(f"Assigning task from {sender_id} to {recipient_id}")
    
    try:
        # Validate task
        if not task.get("title"):
            return {"error": "Task must include a title"}
        
        if not task.get("description"):
            return {"error": "Task must include a description"}
        
        # Create task metadata
        metadata = {
            "task_id": task.get("id", f"task-{uuid.uuid4().hex}"),
            "priority": priority,
            "deadline": deadline,
            "status": "assigned",
            "assigned_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Send task message
        result = await send_message_to_agent(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=json.dumps(task),
            message_type=MessageType.TASK,
            metadata=metadata
        )
        
        if "error" in result:
            return result
        
        # Update recipient agent status to busy
        registry.update_agent(recipient_id, {"status": "busy"})
        
        return {
            "task": task,
            "metadata": metadata,
            "message": result["message"],
            "status": "assigned"
        }
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        return {"error": str(e), "status": "error"}

@mcp.tool(
    annotations={
        "title": "Submit Task Result",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def submit_task_result(
    agent_id: str,
    task_id: str,
    result: Dict[str, Any],
    status: str = "completed"
) -> Dict[str, Any]:
    """Submit the result of a task.
    
    Args:
        agent_id: The ID of the agent submitting the result
        task_id: The ID of the task
        result: The task result
        status: The status of the task (completed, failed, in_progress)
        
    Returns:
        The task result information
    """
    logger.info(f"Submitting task result for task {task_id} from agent {agent_id}")
    
    try:
        # Check if agent exists
        agent = registry.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent with ID '{agent_id}' not found"}
        
        # Find the task message
        task_message = None
        if agent_id in message_queues:
            for message in message_queues[agent_id]:
                if message["type"] == MessageType.TASK and message["metadata"].get("task_id") == task_id:
                    task_message = message
                    break
        
        if not task_message:
            return {"error": f"Task with ID '{task_id}' not found"}
        
        # Create result metadata
        metadata = {
            "task_id": task_id,
            "status": status,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Send result message back to the task sender
        result_message = await send_message_to_agent(
            sender_id=agent_id,
            recipient_id=task_message["sender_id"],
            content=json.dumps(result),
            message_type=MessageType.RESULT,
            metadata=metadata
        )
        
        # Update agent status if task is completed or failed
        if status in ["completed", "failed"]:
            registry.update_agent(agent_id, {"status": "active"})
        
        return {
            "result": result,
            "metadata": metadata,
            "message": result_message.get("message"),
            "status": status
        }
    except Exception as e:
        logger.error(f"Error submitting task result: {e}")
        return {"error": str(e), "status": "error"}

# Main entry point
if __name__ == "__main__":
    # Run the server
    logger.info("Starting agent communication server")
    mcp.run(transport="stdio")
