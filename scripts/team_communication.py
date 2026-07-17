#!/usr/bin/env python3
"""
Team Communication Module - Tools for team-based agent communication.

This module provides tools for agents to communicate with each other in a team context,
including sending messages, creating discussion threads, and sharing files.
"""

import os
import sys
import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("team-communication")

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastmcp import FastMCP

    logger.info("Successfully imported FastMCP")
except ImportError:
    logger.error(
        "Failed to import FastMCP. Please install it with 'pip install fastmcp'"
    )
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
    FILE = "file"


# Initialize agent registry
registry = get_registry()

# Constants for notification messages
SYSTEM_NOTIFICATION_SENDER = "system-notifications"

# In-memory storage for message queues
message_queues = {}

# In-memory storage for conversation history
conversation_history = {}

# In-memory storage for threads
threads = {}

# In-memory storage for unread messages
unread_messages = {}

# Ensure uploads directory exists
uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uploads")
os.makedirs(uploads_dir, exist_ok=True)

# Create the FastMCP server
mcp = FastMCP(
    name="Team Communication", description="Tools for team-based agent communication"
)


# Helper function to notify thread participants about thread creation/updates
async def notify_thread_participants(
    thread_id: str,
    thread_title: str,
    creator_id: str,
    participants: List[str],
    is_new_thread: bool = True,
):
    # Filter out the creator from the notification list
    participants_to_notify = [p for p in participants if p != creator_id]

    if not participants_to_notify:
        return  # No one to notify

    notification_content = (
        f"You have been added to a new thread: '{thread_title}' (ID: {thread_id})"
        if is_new_thread
        else f"You have been added to the thread: '{thread_title}' (ID: {thread_id})"
    )

    if len(participants_to_notify) == 1:
        # Single notification - direct message
        await send_message_to_agent(
            sender_id=SYSTEM_NOTIFICATION_SENDER,
            recipient_id=participants_to_notify[0],
            content=notification_content,
            message_type=MessageType.SYSTEM,
            urgent=True,
        )
    else:
        # Multiple notifications - use broadcast
        await broadcast_message(
            sender_id=SYSTEM_NOTIFICATION_SENDER,
            recipient_ids=participants_to_notify,
            content=notification_content,
            message_type=MessageType.SYSTEM,
            urgent=True,
        )


# Helper function to store a message
async def store_message(
    sender_id: str,
    content: str,
    message_type: str = MessageType.TEXT,
    recipient_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    recipient_ids: Optional[List[str]] = None,
    urgent: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    # Generate message ID
    message_id = f"msg-{uuid.uuid4().hex}"
    timestamp = datetime.now(timezone.utc).isoformat()

    # Create message
    message = {
        "id": message_id,
        "sender_id": sender_id,
        "recipient_id": recipient_id,
        "recipient_ids": recipient_ids,
        "thread_id": thread_id,
        "content": content,
        "type": message_type,
        "urgent": urgent,
        "metadata": metadata or {},
        "timestamp": timestamp,
        "read_by": [sender_id],  # Sender has read the message
    }

    # Store in conversation history
    if sender_id not in conversation_history:
        conversation_history[sender_id] = []

    conversation_history[sender_id].append(message)

    # Store in recipient's conversation history and mark as unread
    if recipient_id:
        if recipient_id not in conversation_history:
            conversation_history[recipient_id] = []

        conversation_history[recipient_id].append(message)

        # Mark as unread for recipient
        if recipient_id not in unread_messages:
            unread_messages[recipient_id] = []

        unread_messages[recipient_id].append(message_id)

    # Store in multiple recipients' conversation histories
    if recipient_ids:
        for rid in recipient_ids:
            if rid not in conversation_history:
                conversation_history[rid] = []

            conversation_history[rid].append(message)

            # Mark as unread for recipient
            if rid not in unread_messages:
                unread_messages[rid] = []

            unread_messages[rid].append(message_id)

    # Store in thread
    if thread_id and thread_id in threads:
        if "messages" not in threads[thread_id]:
            threads[thread_id]["messages"] = []

        threads[thread_id]["messages"].append(message_id)

        # Mark as unread for all thread participants except sender
        for participant in threads[thread_id]["participants"]:
            if participant != sender_id:
                if participant not in unread_messages:
                    unread_messages[participant] = []

                unread_messages[participant].append(message_id)

    # Update agent's last activity
    agent = registry.get_agent(sender_id)
    if agent:
        registry.update_agent(sender_id, {"last_activity": timestamp})

    return message


@mcp.tool(
    annotations={
        "title": "Send Message To Agent",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
async def send_message_to_agent(
    sender_id: str,
    recipient_id: str,
    content: str,
    message_type: str = MessageType.TEXT,
    urgent: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Send a message from one agent to another.

    Args:
        sender_id: The ID of the sender agent
        recipient_id: The ID of the recipient agent
        content: The message content
        message_type: The type of message (text, task, result, status, error, system, file)
        urgent: Whether the message is urgent
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

        # Store message
        message = await store_message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            message_type=message_type,
            urgent=urgent,
            metadata=metadata,
        )

        return {
            "message": message,
            "status": "delivered",
            "timestamp": message["timestamp"],
        }
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {"error": str(e), "status": "error"}


@mcp.tool(
    annotations={
        "title": "Send Message To Thread",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
async def send_message_to_thread(
    sender_id: str,
    thread_id: str,
    content: str,
    message_type: str = MessageType.TEXT,
    urgent: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Send a message to a thread.

    Args:
        sender_id: The ID of the sender agent
        thread_id: The ID of the thread
        content: The message content
        message_type: The type of message (text, task, result, status, error, system, file)
        urgent: Whether the message is urgent
        metadata: Optional metadata for the message

    Returns:
        The sent message information
    """
    logger.info(f"Sending message from {sender_id} to thread {thread_id}")

    try:
        # Check if sender exists
        sender = registry.get_agent(sender_id)
        if not sender:
            return {"error": f"Sender agent with ID '{sender_id}' not found"}

        # Check if thread exists
        if thread_id not in threads:
            return {"error": f"Thread with ID '{thread_id}' not found"}

        # Check if sender is a participant in the thread
        if sender_id not in threads[thread_id]["participants"]:
            return {
                "error": f"Sender agent with ID '{sender_id}' is not a participant in thread '{thread_id}'"
            }

        # Store message
        message = await store_message(
            sender_id=sender_id,
            thread_id=thread_id,
            content=content,
            message_type=message_type,
            urgent=urgent,
            metadata=metadata,
        )

        return {
            "message": message,
            "status": "delivered",
            "timestamp": message["timestamp"],
        }
    except Exception as e:
        logger.error(f"Error sending message to thread: {e}")
        return {"error": str(e), "status": "error"}


@mcp.tool(
    annotations={
        "title": "Broadcast Message",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
async def broadcast_message(
    sender_id: str,
    recipient_ids: List[str],
    content: str,
    message_type: str = MessageType.TEXT,
    urgent: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Send a message to multiple agents simultaneously.

    Args:
        sender_id: The ID of the sender agent
        recipient_ids: List of recipient agent IDs
        content: The message content
        message_type: The type of message (text, task, result, status, error, system, file)
        urgent: Whether the message is urgent
        metadata: Optional metadata for the message

    Returns:
        The sent message information
    """
    logger.info(
        f"Broadcasting message from {sender_id} to {len(recipient_ids)} recipients"
    )

    try:
        # Check if sender exists
        sender = registry.get_agent(sender_id)
        if not sender:
            return {"error": f"Sender agent with ID '{sender_id}' not found"}

        # Check if recipients exist
        for recipient_id in recipient_ids:
            recipient = registry.get_agent(recipient_id)
            if not recipient:
                return {"error": f"Recipient agent with ID '{recipient_id}' not found"}

        # Store message
        message = await store_message(
            sender_id=sender_id,
            recipient_ids=recipient_ids,
            content=content,
            message_type=message_type,
            urgent=urgent,
            metadata=metadata,
        )

        return {
            "message": message,
            "status": "delivered",
            "recipients": recipient_ids,
            "timestamp": message["timestamp"],
        }
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        return {"error": str(e), "status": "error"}


@mcp.tool(
    annotations={"title": "Get Messages", "readOnlyHint": True, "openWorldHint": False}
)
async def get_messages(
    agent_id: str,
    thread_id: Optional[str] = None,
    limit: int = 10,
    since: Optional[str] = None,
    mark_as_read: bool = True,
) -> Dict[str, Any]:
    """Get messages for an agent.

    Args:
        agent_id: The agent ID
        thread_id: Optional thread ID to filter messages
        limit: Maximum number of messages to return
        since: Optional ISO timestamp to get messages after a certain time
        mark_as_read: Whether to mark retrieved messages as read

    Returns:
        List of messages
    """
    logger.info(f"Getting messages for agent: {agent_id}")

    try:
        # Check if agent exists
        agent = registry.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent with ID '{agent_id}' not found"}

        # Get agent's threads
        agent_threads = []
        for thread_id, thread in threads.items():
            if agent_id in thread["participants"]:
                agent_threads.append(thread_id)

        # Filter messages
        if agent_id not in conversation_history:
            return {"messages": [], "count": 0}

        relevant_messages = []
        for message in conversation_history[agent_id]:
            # Filter by timestamp if provided
            if since and message["timestamp"] < since:
                continue

            # Filter by thread if provided
            if thread_id and message.get("thread_id") != thread_id:
                continue

            # Include direct messages if no thread filter
            if not thread_id and message.get("recipient_id") == agent_id:
                relevant_messages.append(message)
                continue

            # Include broadcast messages if no thread filter
            if (
                not thread_id
                and message.get("recipient_ids")
                and agent_id in message.get("recipient_ids", [])
            ):
                relevant_messages.append(message)
                continue

            # Include thread messages
            if message.get("thread_id") and (
                not thread_id or message.get("thread_id") == thread_id
            ):
                if message.get("thread_id") in agent_threads:
                    relevant_messages.append(message)
                    continue

        # Sort by timestamp (newest first)
        relevant_messages.sort(key=lambda m: m["timestamp"], reverse=True)

        # Apply limit
        limited_messages = relevant_messages[:limit]

        # Mark messages as read if requested
        if mark_as_read and agent_id in unread_messages:
            message_ids = [m["id"] for m in limited_messages]
            unread_messages[agent_id] = [
                mid for mid in unread_messages[agent_id] if mid not in message_ids
            ]

            # Update read_by field in messages
            for message in limited_messages:
                if agent_id not in message["read_by"]:
                    message["read_by"].append(agent_id)

        return {
            "messages": limited_messages,
            "count": len(limited_messages),
            "total": len(relevant_messages),
        }
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return {"error": str(e), "status": "error"}


@mcp.tool(
    annotations={
        "title": "Create Thread",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
async def create_thread(
    creator_id: str,
    title: str,
    participants: List[str],
    initial_message: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new discussion thread.

    Args:
        creator_id: The ID of the agent creating the thread
        title: A descriptive title for the thread
        participants: List of agent IDs to include in the thread
        initial_message: Optional first message to post in the thread

    Returns:
        The created thread information
    """
    logger.info(f"Creating thread: {title} by {creator_id}")

    try:
        # Check if creator exists
        creator = registry.get_agent(creator_id)
        if not creator:
            return {"error": f"Creator agent with ID '{creator_id}' not found"}

        # Check if participants exist
        for participant_id in participants:
            participant = registry.get_agent(participant_id)
            if not participant:
                return {
                    "error": f"Participant agent with ID '{participant_id}' not found"
                }

        # Ensure creator is in participants
        if creator_id not in participants:
            participants.append(creator_id)

        # Generate thread ID
        thread_id = f"thread-{uuid.uuid4().hex}"

        # Create thread
        timestamp = datetime.now(timezone.utc).isoformat()

        thread = {
            "id": thread_id,
            "title": title,
            "creator_id": creator_id,
            "participants": participants,
            "created_at": timestamp,
            "updated_at": timestamp,
            "messages": [],
        }

        # Store thread
        threads[thread_id] = thread

        # Add initial message if provided
        first_message = None
        if initial_message:
            first_message = await store_message(
                sender_id=creator_id,
                thread_id=thread_id,
                content=initial_message,
                message_type=MessageType.TEXT,
                urgent=False,
            )

        # Send notifications to participants
        await notify_thread_participants(
            thread_id=thread_id,
            thread_title=title,
            creator_id=creator_id,
            participants=participants,
            is_new_thread=True,
        )

        return {"thread": thread, "initial_message": first_message, "status": "created"}
    except Exception as e:
        logger.error(f"Error creating thread: {e}")
        return {"error": str(e), "status": "error"}


@mcp.tool(
    annotations={
        "title": "Join Thread",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
async def join_thread(agent_id: str, thread_id: str) -> Dict[str, Any]:
    """Join an existing thread.

    Args:
        agent_id: The ID of the agent joining the thread
        thread_id: The ID of the thread to join

    Returns:
        The result of joining the thread
    """
    logger.info(f"Agent {agent_id} joining thread {thread_id}")

    try:
        # Check if agent exists
        agent = registry.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent with ID '{agent_id}' not found"}

        # Check if thread exists
        if thread_id not in threads:
            return {"error": f"Thread with ID '{thread_id}' not found"}

        # Check if agent is already a participant
        if agent_id in threads[thread_id]["participants"]:
            return {
                "thread_id": thread_id,
                "agent_id": agent_id,
                "status": "already_participant",
            }

        # Add agent to participants
        threads[thread_id]["participants"].append(agent_id)
        threads[thread_id]["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Send notification to the agent who just joined
        await store_message(
            sender_id=SYSTEM_NOTIFICATION_SENDER,
            recipient_id=agent_id,
            content=f"You have joined the thread: '{threads[thread_id]['title']}' (ID: {thread_id})",
            message_type=MessageType.SYSTEM,
            urgent=True,
        )

        # Notify other participants that a new agent has joined
        await store_message(
            sender_id=SYSTEM_NOTIFICATION_SENDER,
            thread_id=thread_id,
            content=f"Agent {agent_id} has joined the thread",
            message_type=MessageType.SYSTEM,
            urgent=False,
        )

        return {"thread_id": thread_id, "agent_id": agent_id, "status": "joined"}
    except Exception as e:
        logger.error(f"Error joining thread: {e}")
        return {"error": str(e), "status": "error"}


@mcp.tool(
    annotations={
        "title": "Get Thread Details",
        "readOnlyHint": True,
        "openWorldHint": False,
    }
)
async def get_thread_details(
    thread_id: str, include_messages: bool = False, message_limit: int = 10
) -> Dict[str, Any]:
    """Get details about a thread.

    Args:
        thread_id: The ID of the thread
        include_messages: Whether to include recent messages in the thread
        message_limit: Maximum number of messages to include if include_messages is True

    Returns:
        The thread details
    """
    logger.info(f"Getting details for thread: {thread_id}")

    try:
        # Check if thread exists
        if thread_id not in threads:
            return {"error": f"Thread with ID '{thread_id}' not found"}

        thread = threads[thread_id]

        # Create thread details
        thread_details = {
            "id": thread["id"],
            "title": thread["title"],
            "creator_id": thread["creator_id"],
            "participants": thread["participants"],
            "created_at": thread["created_at"],
            "updated_at": thread["updated_at"],
            "message_count": len(thread["messages"]),
        }

        # Include messages if requested
        if include_messages:
            # Get message IDs from thread
            message_ids = thread["messages"]

            # Get messages from conversation history
            messages = []
            for agent_id in thread["participants"]:
                if agent_id in conversation_history:
                    for message in conversation_history[agent_id]:
                        if (
                            message.get("thread_id") == thread_id
                            and message["id"] in message_ids
                        ):
                            if message not in messages:
                                messages.append(message)

            # Sort by timestamp (newest first)
            messages.sort(key=lambda m: m["timestamp"], reverse=True)

            # Apply limit
            limited_messages = messages[:message_limit]

            thread_details["messages"] = limited_messages

        return {"thread": thread_details}
    except Exception as e:
        logger.error(f"Error getting thread details: {e}")
        return {"error": str(e), "status": "error"}


@mcp.tool(
    annotations={
        "title": "Check New Messages",
        "readOnlyHint": True,
        "openWorldHint": False,
    }
)
async def check_new_messages(agent_id: str) -> Dict[str, Any]:
    """Check for unread messages.

    Args:
        agent_id: The agent ID

    Returns:
        Count of unread messages
    """
    logger.info(f"Checking new messages for agent: {agent_id}")

    try:
        # Check if agent exists
        agent = registry.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent with ID '{agent_id}' not found"}

        # Get unread message count
        unread_count = 0
        if agent_id in unread_messages:
            unread_count = len(unread_messages[agent_id])

        return {"agent_id": agent_id, "unread_count": unread_count}
    except Exception as e:
        logger.error(f"Error checking new messages: {e}")
        return {"error": str(e), "status": "error"}


@mcp.tool(
    annotations={
        "title": "Transfer File",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
async def transfer_file(
    sender_id: str,
    recipient_id: str,
    source_path: str,
    destination_filename: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Transfer a file from one agent to another.

    Args:
        sender_id: The ID of the sender agent
        recipient_id: The ID of the recipient agent
        source_path: The path to the file to transfer
        destination_filename: Optional custom filename for the transferred file
        description: Optional description of the file

    Returns:
        The result of the file transfer
    """
    logger.info(f"Transferring file from {sender_id} to {recipient_id}")

    try:
        # Check if sender exists
        sender = registry.get_agent(sender_id)
        if not sender:
            return {"error": f"Sender agent with ID '{sender_id}' not found"}

        # Check if recipient exists
        recipient = registry.get_agent(recipient_id)
        if not recipient:
            return {"error": f"Recipient agent with ID '{recipient_id}' not found"}

        # Check if source file exists
        if not os.path.exists(source_path):
            return {"error": f"Source file '{source_path}' not found"}

        # Generate safe filename
        filename = destination_filename or os.path.basename(source_path)
        safe_filename = os.path.basename(filename)

        # Generate unique destination path
        file_id = uuid.uuid4().hex
        destination_path = os.path.join(uploads_dir, f"{file_id}_{safe_filename}")

        # Copy file
        shutil.copy2(source_path, destination_path)

        # Create message content
        message_content = f"File transfer: {safe_filename}"
        if description:
            message_content += f"\nDescription: {description}"
        message_content += f"\nFile ID: {file_id}"

        # Send notification message
        notification_message = await store_message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=message_content,
            message_type=MessageType.FILE,
            urgent=False,
            metadata={
                "file_id": file_id,
                "filename": safe_filename,
                "server_path": destination_path,
                "description": description,
            },
        )

        return {
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "filename": safe_filename,
            "file_id": file_id,
            "server_path": destination_path,
            "description": description,
            "notification_message_id": notification_message["id"],
            "timestamp": notification_message["timestamp"],
        }
    except Exception as e:
        logger.error(f"Error transferring file: {e}")
        return {"error": str(e), "status": "error"}


# Main entry point
if __name__ == "__main__":
    # Run the server
    logger.info("Starting team communication server")
    mcp.run(transport="stdio")
