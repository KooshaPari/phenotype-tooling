"""
CRUD operations for the SWE agent database.
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
import uuid
import json

from .models import Agent, Conversation


def create_agent(db: Session, agent_data: Dict[str, Any]) -> Agent:
    """
    Create a new agent.

    Args:
        db: Database session.
        agent_data: Agent data.

    Returns:
        The created agent.
    """
    agent_id = agent_data.get("agent_id") or f"agent-{uuid.uuid4().hex}"
    db_agent = Agent(
        agent_id=agent_id,
        name=agent_data.get("name"),
        description=agent_data.get("description"),
        llm_model_id=agent_data.get("llm_model_id"),
        mcp_tools_config_path=agent_data.get("mcp_tools_config_path"),
        initial_prompt=agent_data.get("initial_prompt"),
        status=agent_data.get("status", "inactive"),
        config=agent_data.get("config"),
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def get_agent(db: Session, agent_id: str) -> Optional[Agent]:
    """
    Get an agent by ID.

    Args:
        db: Database session.
        agent_id: Agent ID.

    Returns:
        The agent, or None if not found.
    """
    return db.query(Agent).filter(Agent.agent_id == agent_id).first()


def get_agents(db: Session, skip: int = 0, limit: int = 100) -> List[Agent]:
    """
    Get all agents.

    Args:
        db: Database session.
        skip: Number of agents to skip.
        limit: Maximum number of agents to return.

    Returns:
        List of agents.
    """
    return db.query(Agent).offset(skip).limit(limit).all()


def update_agent(
    db: Session, agent_id: str, agent_data: Dict[str, Any]
) -> Optional[Agent]:
    """
    Update an agent.

    Args:
        db: Database session.
        agent_id: Agent ID.
        agent_data: Agent data.

    Returns:
        The updated agent, or None if not found.
    """
    db_agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if db_agent:
        for key, value in agent_data.items():
            if hasattr(db_agent, key):
                setattr(db_agent, key, value)
        db.commit()
        db.refresh(db_agent)
    return db_agent


def delete_agent(db: Session, agent_id: str) -> bool:
    """
    Delete an agent.

    Args:
        db: Database session.
        agent_id: Agent ID.

    Returns:
        True if the agent was deleted, False otherwise.
    """
    db_agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return True
    return False


def create_conversation(db: Session, conversation_data: Dict[str, Any]) -> Conversation:
    """
    Create a new conversation.

    Args:
        db: Database session.
        conversation_data: Conversation data.

    Returns:
        The created conversation.
    """
    conversation_id = (
        conversation_data.get("conversation_id") or f"conv-{uuid.uuid4().hex}"
    )
    db_conversation = Conversation(
        conversation_id=conversation_id,
        agent_id=conversation_data.get("agent_id"),
        messages=conversation_data.get("messages", []),
        meta_data=conversation_data.get(
            "metadata"
        ),  # Changed from metadata to meta_data
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def get_conversation(db: Session, conversation_id: str) -> Optional[Conversation]:
    """
    Get a conversation by ID.

    Args:
        db: Database session.
        conversation_id: Conversation ID.

    Returns:
        The conversation, or None if not found.
    """
    return (
        db.query(Conversation)
        .filter(Conversation.conversation_id == conversation_id)
        .first()
    )


def get_agent_conversations(
    db: Session, agent_id: str, skip: int = 0, limit: int = 100
) -> List[Conversation]:
    """
    Get all conversations for an agent.

    Args:
        db: Database session.
        agent_id: Agent ID.
        skip: Number of conversations to skip.
        limit: Maximum number of conversations to return.

    Returns:
        List of conversations.
    """
    return (
        db.query(Conversation)
        .filter(Conversation.agent_id == agent_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_conversation(
    db: Session, conversation_id: str, conversation_data: Dict[str, Any]
) -> Optional[Conversation]:
    """
    Update a conversation.

    Args:
        db: Database session.
        conversation_id: Conversation ID.
        conversation_data: Conversation data.

    Returns:
        The updated conversation, or None if not found.
    """
    db_conversation = (
        db.query(Conversation)
        .filter(Conversation.conversation_id == conversation_id)
        .first()
    )
    if db_conversation:
        for key, value in conversation_data.items():
            if hasattr(db_conversation, key):
                setattr(db_conversation, key, value)
        db.commit()
        db.refresh(db_conversation)
    return db_conversation


def delete_conversation(db: Session, conversation_id: str) -> bool:
    """
    Delete a conversation.

    Args:
        db: Database session.
        conversation_id: Conversation ID.

    Returns:
        True if the conversation was deleted, False otherwise.
    """
    db_conversation = (
        db.query(Conversation)
        .filter(Conversation.conversation_id == conversation_id)
        .first()
    )
    if db_conversation:
        db.delete(db_conversation)
        db.commit()
        return True
    return False
