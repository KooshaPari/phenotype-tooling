"""
Agent Communication Hub for facilitating communication between agents.

This module provides functionality for agents to communicate with each other
in a swarm-like system, integrating with team-communications MCP tools.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime

from ..utils.logging import logger
from .agent_manager import agent_manager


class AgentCommunicationHub:
    """
    Hub for facilitating communication between agents.
    """

    def __init__(self):
        """Initialize the agent communication hub."""
        self.message_queues: Dict[str, asyncio.Queue] = {}
        self.message_history: Dict[str, List[Dict[str, Any]]] = {}
        self.subscribers: Dict[
            str, List[Callable[[Dict[str, Any]], Awaitable[None]]]
        ] = {}
        self.logger = logger

    def _get_conversation_id(self, sender_id: str, recipient_id: str) -> str:
        """
        Get a unique conversation ID for a pair of agents.

        Args:
            sender_id: The sender agent ID.
            recipient_id: The recipient agent ID.

        Returns:
            A unique conversation ID.
        """
        # Sort the agent IDs to ensure the same conversation ID regardless of sender/recipient
        agent_ids = sorted([sender_id, recipient_id])
        return f"conversation-{agent_ids[0]}-{agent_ids[1]}"

    async def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a message from one agent to another.

        Args:
            sender_id: The sender agent ID.
            recipient_id: The recipient agent ID.
            content: The message content.
            metadata: Optional message metadata.

        Returns:
            The message that was sent.
        """
        # Create the message
        message = {
            "message_id": f"msg-{uuid.uuid4().hex}",
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Get the conversation ID
        conversation_id = self._get_conversation_id(sender_id, recipient_id)

        # Initialize the message queue and history if they don't exist
        if conversation_id not in self.message_queues:
            self.message_queues[conversation_id] = asyncio.Queue()
            self.message_history[conversation_id] = []

        # Add the message to the queue and history
        await self.message_queues[conversation_id].put(message)
        self.message_history[conversation_id].append(message)

        # Notify subscribers
        if recipient_id in self.subscribers:
            for callback in self.subscribers[recipient_id]:
                try:
                    await callback(message)
                except Exception as e:
                    self.logger.error(
                        f"Error notifying subscriber for agent {recipient_id}: {e}"
                    )

        self.logger.info(
            f"Message sent from {sender_id} to {recipient_id}: {message['message_id']}"
        )

        return message

    async def receive_messages(
        self,
        agent_id: str,
        other_agent_id: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Receive messages for an agent.

        Args:
            agent_id: The agent ID.
            other_agent_id: Optional other agent ID to filter messages.
            timeout: Optional timeout in seconds.

        Returns:
            A list of messages.
        """
        messages = []

        if other_agent_id:
            # Get messages from a specific conversation
            conversation_id = self._get_conversation_id(agent_id, other_agent_id)

            if conversation_id in self.message_queues:
                # Get all messages from the queue
                try:
                    while True:
                        if timeout:
                            message = await asyncio.wait_for(
                                self.message_queues[conversation_id].get(),
                                timeout=timeout,
                            )
                        else:
                            message = self.message_queues[conversation_id].get_nowait()

                        if message["recipient_id"] == agent_id:
                            messages.append(message)

                        self.message_queues[conversation_id].task_done()
                except (asyncio.QueueEmpty, asyncio.TimeoutError):
                    pass
        else:
            # Get messages from all conversations
            for conversation_id, queue in self.message_queues.items():
                try:
                    while True:
                        message = queue.get_nowait()

                        if message["recipient_id"] == agent_id:
                            messages.append(message)

                        queue.task_done()
                except asyncio.QueueEmpty:
                    pass

        return messages

    def get_message_history(
        self,
        agent_id: str,
        other_agent_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get message history for an agent.

        Args:
            agent_id: The agent ID.
            other_agent_id: Optional other agent ID to filter messages.
            limit: Optional limit on the number of messages to return.

        Returns:
            A list of messages.
        """
        messages = []

        if other_agent_id:
            # Get messages from a specific conversation
            conversation_id = self._get_conversation_id(agent_id, other_agent_id)

            if conversation_id in self.message_history:
                # Get messages where the agent is either the sender or recipient
                for message in self.message_history[conversation_id]:
                    if (
                        message["sender_id"] == agent_id
                        or message["recipient_id"] == agent_id
                    ):
                        messages.append(message)
        else:
            # Get messages from all conversations
            for conversation_id, history in self.message_history.items():
                for message in history:
                    if (
                        message["sender_id"] == agent_id
                        or message["recipient_id"] == agent_id
                    ):
                        messages.append(message)

        # Sort messages by timestamp
        messages.sort(key=lambda m: m["timestamp"])

        # Apply limit if specified
        if limit is not None and limit > 0:
            messages = messages[-limit:]

        return messages

    async def subscribe(
        self,
        agent_id: str,
        callback: Callable[[Dict[str, Any]], Awaitable[None]],
    ) -> None:
        """
        Subscribe to messages for an agent.

        Args:
            agent_id: The agent ID.
            callback: The callback function to call when a message is received.
        """
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []

        self.subscribers[agent_id].append(callback)

        self.logger.info(f"Subscribed to messages for agent {agent_id}")

    async def unsubscribe(
        self,
        agent_id: str,
        callback: Callable[[Dict[str, Any]], Awaitable[None]],
    ) -> bool:
        """
        Unsubscribe from messages for an agent.

        Args:
            agent_id: The agent ID.
            callback: The callback function to remove.

        Returns:
            True if the callback was removed, False otherwise.
        """
        if agent_id in self.subscribers and callback in self.subscribers[agent_id]:
            self.subscribers[agent_id].remove(callback)

            if not self.subscribers[agent_id]:
                del self.subscribers[agent_id]

            self.logger.info(f"Unsubscribed from messages for agent {agent_id}")

            return True

        return False

    async def broadcast_message(
        self,
        sender_id: str,
        content: str,
        recipient_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Broadcast a message to multiple agents.

        Args:
            sender_id: The sender agent ID.
            content: The message content.
            recipient_ids: Optional list of recipient agent IDs. If None, send to all agents.
            metadata: Optional message metadata.

        Returns:
            A list of messages that were sent.
        """
        messages = []

        # If no recipient IDs are specified, get all agent IDs
        if recipient_ids is None:
            # Get all agents from the agent manager
            agents = await agent_manager.list_agents()
            recipient_ids = [
                agent["agent_id"] for agent in agents if agent["agent_id"] != sender_id
            ]

        # Send the message to each recipient
        for recipient_id in recipient_ids:
            message = await self.send_message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                content=content,
                metadata=metadata,
            )

            messages.append(message)

        return messages

    async def get_messages(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Get new messages for an agent (convenience method for autonomous loops).

        Args:
            agent_id: The agent ID.

        Returns:
            A list of new messages for the agent.
        """
        return await self.receive_messages(agent_id, timeout=0.1)

    async def register_agent(
        self,
        agent_id: str,
        name: str,
        role: str,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register an agent with the communication hub.

        Args:
            agent_id: The agent ID.
            name: The agent name.
            role: The agent role.
            capabilities: List of agent capabilities.
            metadata: Optional metadata.
        """
        # For now, just log the registration
        # In a full implementation, this might store agent info
        self.logger.info(f"Registered agent {agent_id} ({name}) with role {role}")

    async def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from the communication hub.

        Args:
            agent_id: The agent ID.
        """
        # Clean up any subscriptions
        if agent_id in self.subscribers:
            del self.subscribers[agent_id]

        # Clean up message queues and history for this agent
        conversations_to_remove = []
        for conversation_id in self.message_queues.keys():
            if agent_id in conversation_id:
                conversations_to_remove.append(conversation_id)

        for conversation_id in conversations_to_remove:
            if conversation_id in self.message_queues:
                del self.message_queues[conversation_id]
            if conversation_id in self.message_history:
                del self.message_history[conversation_id]

        self.logger.info(f"Unregistered agent {agent_id}")


# Create a singleton instance
communication_hub = AgentCommunicationHub()


# Convenience function for sending messages
async def send_message_to_agent(
    sender_id: str,
    recipient_id: str,
    content: str,
    message_type: str = "text",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience function to send a message to an agent.

    Args:
        sender_id: The sender agent ID.
        recipient_id: The recipient agent ID.
        content: The message content.
        message_type: The type of message (text, task, result, etc.).
        metadata: Optional message metadata.

    Returns:
        The message that was sent.
    """
    if metadata is None:
        metadata = {}

    metadata["type"] = message_type

    return await communication_hub.send_message(
        sender_id=sender_id,
        recipient_id=recipient_id,
        content=content,
        metadata=metadata,
    )
