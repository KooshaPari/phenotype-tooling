"""
API Endpoints for Agent Management (CRUD operations) and Agent Communication.

This module provides REST API endpoints for creating, retrieving, updating, and deleting agents,
as well as for agent communication in a swarm-like system.
"""

import uuid
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Callable, Awaitable
from sqlalchemy.orm import Session

from ..agent import SWEAgent
from ..db.models import get_db
from ..db import crud
from ..utils.logging import logger, request_logger
from ..services.agent_communication import communication_hub

router = APIRouter()

# In-memory cache for agent instances
AGENT_INSTANCES: Dict[str, SWEAgent] = {}


# --- Pydantic Models for Agent Configuration and Responses ---
class AgentInstanceConfig(BaseModel):
    agent_id: str = Field(default_factory=lambda: f"agent-{uuid.uuid4().hex}")
    name: str
    description: Optional[str] = None
    llm_model_id: str  # e.g., "gpt-4", "claude-2"
    mcp_tools_config_path: Optional[str] = (
        None  # Path to a specific MCP config for this agent
    )
    initial_prompt: Optional[str] = None
    # Add other agent-specific configurations here
    # For example, workspace path, data source connections, etc.
    status: str = "inactive"  # e.g., inactive, active, error


class CreateAgentRequest(BaseModel):
    name: str
    description: Optional[str] = None
    llm_model_id: str
    mcp_tools_config_path: Optional[str] = None
    initial_prompt: Optional[str] = None


class UpdateAgentRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    llm_model_id: Optional[str] = None
    mcp_tools_config_path: Optional[str] = None
    initial_prompt: Optional[str] = None
    status: Optional[str] = None


class AgentListResponse(BaseModel):
    object: str = "list"
    data: List[AgentInstanceConfig]


class AgentMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None


class AgentCompletionRequest(BaseModel):
    messages: List[Union[AgentMessage, str]]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None


# --- Agent Communication Models ---


class MessageSend(BaseModel):
    """Model for sending a message between agents."""

    sender_id: str = Field(..., description="The sender agent ID")
    recipient_id: str = Field(..., description="The recipient agent ID")
    content: str = Field(..., description="The message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Message metadata")


class MessageBroadcast(BaseModel):
    """Model for broadcasting a message to multiple agents."""

    sender_id: str = Field(..., description="The sender agent ID")
    content: str = Field(..., description="The message content")
    recipient_ids: Optional[List[str]] = Field(
        None, description="List of recipient agent IDs"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Message metadata")


# --- Agent CRUD Endpoints ---


@router.post(
    "/v1/agents", response_model=AgentInstanceConfig, status_code=201, tags=["Agents"]
)
async def create_agent(
    agent_data: CreateAgentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Creates a new agent instance.
    """
    # Generate a unique ID for the agent
    new_agent_id = f"agent-{uuid.uuid4().hex}"

    # Create the agent config
    agent_config_dict = {
        "agent_id": new_agent_id,
        "name": agent_data.name,
        "description": agent_data.description,
        "llm_model_id": agent_data.llm_model_id,
        "mcp_tools_config_path": agent_data.mcp_tools_config_path,
        "initial_prompt": agent_data.initial_prompt,
        "status": "creating",  # Initial status
        "config": agent_data.model_dump(),
    }

    # Create the agent in the database
    db_agent = crud.create_agent(db, agent_config_dict)

    # Convert to Pydantic model for response
    agent_config = AgentInstanceConfig(
        agent_id=db_agent.agent_id,
        name=db_agent.name,
        description=db_agent.description,
        llm_model_id=db_agent.llm_model_id,
        mcp_tools_config_path=db_agent.mcp_tools_config_path,
        initial_prompt=db_agent.initial_prompt,
        status=db_agent.status,
    )

    # Initialize the agent in the background
    background_tasks.add_task(initialize_agent, new_agent_id, agent_config)

    # Log the creation
    logger.info(f"Agent created: {new_agent_id}")
    request_logger.log_request(
        request_id=new_agent_id,
        endpoint="/v1/agents",
        method="POST",
        data=agent_data.model_dump(),
    )

    return agent_config


async def initialize_agent(agent_id: str, config: AgentInstanceConfig):
    """
    Initialize an agent instance in the background.

    Args:
        agent_id: The agent ID.
        config: The agent configuration.
    """
    # Get a database session
    db = next(get_db())

    try:
        # Create and initialize the agent
        agent = SWEAgent(
            model_name=config.llm_model_id, system_prompt=config.initial_prompt
        )
        await agent.initialize()

        # Store the agent instance in memory
        AGENT_INSTANCES[agent_id] = agent

        # Update the agent status in the database
        agent_update = {"status": "active"}
        crud.update_agent(db, agent_id, agent_update)

        # Log the successful initialization
        logger.info(f"Agent {agent_id} initialized successfully.")
    except Exception as e:
        # Update the agent status to error in the database
        agent_update = {"status": "error"}
        crud.update_agent(db, agent_id, agent_update)

        # Log the error
        logger.error(f"Error initializing agent {agent_id}: {e}")
    finally:
        # Close the database session
        db.close()


@router.get("/v1/agents", response_model=AgentListResponse, tags=["Agents"])
async def list_agents(db: Session = Depends(get_db)):
    """
    Lists all configured agent instances.
    """
    # Get all agents from the database
    db_agents = crud.get_agents(db)

    # Convert to Pydantic models
    agents = [
        AgentInstanceConfig(
            agent_id=agent.agent_id,
            name=agent.name,
            description=agent.description,
            llm_model_id=agent.llm_model_id,
            mcp_tools_config_path=agent.mcp_tools_config_path,
            initial_prompt=agent.initial_prompt,
            status=agent.status,
        )
        for agent in db_agents
    ]

    # Log the request
    logger.info(f"Listed {len(agents)} agents")

    return AgentListResponse(data=agents)


@router.get(
    "/v1/agents/{agent_id}", response_model=AgentInstanceConfig, tags=["Agents"]
)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """
    Retrieves details for a specific agent instance.
    """
    # Get the agent from the database
    db_agent = crud.get_agent(db, agent_id)
    if not db_agent:
        # Log the error
        logger.warning(f"Agent not found: {agent_id}")
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # Convert to Pydantic model
    agent = AgentInstanceConfig(
        agent_id=db_agent.agent_id,
        name=db_agent.name,
        description=db_agent.description,
        llm_model_id=db_agent.llm_model_id,
        mcp_tools_config_path=db_agent.mcp_tools_config_path,
        initial_prompt=db_agent.initial_prompt,
        status=db_agent.status,
    )

    # Log the request
    logger.info(f"Retrieved agent: {agent_id}")

    return agent


@router.put(
    "/v1/agents/{agent_id}", response_model=AgentInstanceConfig, tags=["Agents"]
)
async def update_agent(
    agent_id: str,
    update_data: UpdateAgentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Updates an existing agent instance.
    """
    # Get the agent from the database
    db_agent = crud.get_agent(db, agent_id)
    if not db_agent:
        # Log the error
        logger.warning(f"Agent not found for update: {agent_id}")
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # Extract the update data
    update_data_dict = update_data.model_dump(exclude_unset=True)

    # Check if we need to reinitialize the agent
    reinitialize = False
    if (
        "llm_model_id" in update_data_dict
        or "initial_prompt" in update_data_dict
        or "mcp_tools_config_path" in update_data_dict
    ):
        reinitialize = True
        update_data_dict["status"] = "updating"

    # Update the agent in the database
    updated_db_agent = crud.update_agent(db, agent_id, update_data_dict)

    # Convert to Pydantic model for response
    agent = AgentInstanceConfig(
        agent_id=updated_db_agent.agent_id,
        name=updated_db_agent.name,
        description=updated_db_agent.description,
        llm_model_id=updated_db_agent.llm_model_id,
        mcp_tools_config_path=updated_db_agent.mcp_tools_config_path,
        initial_prompt=updated_db_agent.initial_prompt,
        status=updated_db_agent.status,
    )

    # Reinitialize the agent if needed
    if reinitialize and agent_id in AGENT_INSTANCES:
        background_tasks.add_task(initialize_agent, agent_id, agent)

    # Log the update
    logger.info(f"Updated agent: {agent_id}, reinitialize: {reinitialize}")
    request_logger.log_request(
        request_id=agent_id,
        endpoint=f"/v1/agents/{agent_id}",
        method="PUT",
        data=update_data.model_dump(),
    )

    return agent


@router.delete("/v1/agents/{agent_id}", status_code=204, tags=["Agents"])
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """
    Deletes an agent instance.
    """
    # Check if the agent exists in the database
    db_agent = crud.get_agent(db, agent_id)
    if not db_agent:
        # Log the error
        logger.warning(f"Agent not found for deletion: {agent_id}")
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # Delete the agent from the database
    success = crud.delete_agent(db, agent_id)
    if not success:
        # Log the error
        logger.error(f"Failed to delete agent from database: {agent_id}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete agent '{agent_id}'"
        )

    # Remove the agent instance from memory if it exists
    if agent_id in AGENT_INSTANCES:
        del AGENT_INSTANCES[agent_id]

    # Log the deletion
    logger.info(f"Deleted agent: {agent_id}")
    request_logger.log_request(
        request_id=agent_id,
        endpoint=f"/v1/agents/{agent_id}",
        method="DELETE",
        data={"agent_id": agent_id},
    )

    return  # No content response


@router.post("/v1/agents/{agent_id}/completions", tags=["Agents"])
async def agent_completion(
    agent_id: str, request: AgentCompletionRequest, db: Session = Depends(get_db)
):
    """
    Invoke an agent with a set of messages.
    """
    # Generate a request ID for logging
    request_id = f"req-{uuid.uuid4().hex}"

    # Check if the agent exists in the database
    db_agent = crud.get_agent(db, agent_id)
    if not db_agent:
        # Log the error
        logger.warning(f"Agent not found for completion: {agent_id}")
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # Check if the agent is active
    if db_agent.status != "active":
        # Log the error
        logger.warning(
            f"Agent not active for completion: {agent_id}, status: {db_agent.status}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Agent '{agent_id}' is not active (status: {db_agent.status})",
        )

    # Get the agent instance from memory
    if agent_id not in AGENT_INSTANCES:
        # Log the error
        logger.error(f"Agent instance not found in memory: {agent_id}")
        raise HTTPException(
            status_code=500, detail=f"Agent '{agent_id}' instance not found"
        )

    agent = AGENT_INSTANCES[agent_id]

    # Convert messages to the format expected by the agent
    messages = []
    for msg in request.messages:
        if isinstance(msg, str):
            messages.append({"role": "user", "content": msg})
        else:
            messages.append(
                {
                    "role": msg.role,
                    "content": msg.content,
                    **({"name": msg.name} if msg.name else {}),
                    **({"tool_call_id": msg.tool_call_id} if msg.tool_call_id else {}),
                }
            )

    # Prepare the agent input
    agent_input = {
        "messages": messages,
        "agent_config": {
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "agent_id": agent_id,
            "request_id": request_id,
        },
    }

    # Log the request
    logger.info(f"Agent completion request: {request_id}, agent: {agent_id}")
    request_logger.log_request(
        request_id=request_id,
        endpoint=f"/v1/agents/{agent_id}/completions",
        method="POST",
        data={"agent_id": agent_id, "messages_count": len(messages)},
    )

    # Stream the response if requested
    if request.stream:
        from fastapi.responses import StreamingResponse

        async def stream_generator():
            try:
                async for chunk in agent.stream(agent_input):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"

                # Log the successful completion
                logger.info(f"Agent completion streaming finished: {request_id}")
                request_logger.log_response(
                    request_id=request_id,
                    status_code=200,
                    data={"status": "success", "streaming": True},
                )
            except Exception as e:
                # Log the error
                logger.error(
                    f"Error in agent completion streaming: {request_id}, error: {str(e)}"
                )
                request_logger.log_response(
                    request_id=request_id,
                    status_code=500,
                    data={"status": "error", "error": str(e)},
                )
                yield f'data: {{"error": "{str(e)}"}}\n\n'
                yield "data: [DONE]\n\n"

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    # Otherwise, return the full response
    try:
        response = await agent.invoke(agent_input)

        # Log the successful completion
        logger.info(f"Agent completion successful: {request_id}")
        request_logger.log_response(
            request_id=request_id, status_code=200, data={"status": "success"}
        )

        return response
    except Exception as e:
        # Log the error
        logger.error(f"Error invoking agent {agent_id}: {e}")
        request_logger.log_response(
            request_id=request_id,
            status_code=500,
            data={"status": "error", "error": str(e)},
        )

        raise HTTPException(status_code=500, detail=str(e))


# --- Agent Communication Endpoints ---


@router.post("/v1/agents/messages/send", tags=["Agent Communication"])
async def send_message(message_data: MessageSend):
    """
    Send a message from one agent to another.

    Args:
        message_data: The message data.

    Returns:
        The sent message.
    """
    try:
        # Check if the sender agent exists
        sender_db = next(get_db())
        sender_agent = crud.get_agent(sender_db, message_data.sender_id)
        if not sender_agent:
            # Log the error
            logger.warning(f"Sender agent not found: {message_data.sender_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Sender agent '{message_data.sender_id}' not found",
            )

        # Check if the recipient agent exists
        recipient_db = next(get_db())
        recipient_agent = crud.get_agent(recipient_db, message_data.recipient_id)
        if not recipient_agent:
            # Log the error
            logger.warning(f"Recipient agent not found: {message_data.recipient_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Recipient agent '{message_data.recipient_id}' not found",
            )

        # Send the message
        message = await communication_hub.send_message(
            sender_id=message_data.sender_id,
            recipient_id=message_data.recipient_id,
            content=message_data.content,
            metadata=message_data.metadata,
        )

        # Log the message
        logger.info(
            f"Message sent from {message_data.sender_id} to {message_data.recipient_id}: {message['message_id']}"
        )

        return message
    except HTTPException:
        raise
    except Exception as e:
        # Log the error
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/v1/agents/messages/broadcast", tags=["Agent Communication"])
async def broadcast_message(message_data: MessageBroadcast):
    """
    Broadcast a message to multiple agents.

    Args:
        message_data: The message data.

    Returns:
        The sent messages.
    """
    try:
        # Check if the sender agent exists
        sender_db = next(get_db())
        sender_agent = crud.get_agent(sender_db, message_data.sender_id)
        if not sender_agent:
            # Log the error
            logger.warning(f"Sender agent not found: {message_data.sender_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Sender agent '{message_data.sender_id}' not found",
            )

        # If recipient IDs are specified, check if they exist
        if message_data.recipient_ids:
            recipient_db = next(get_db())
            for recipient_id in message_data.recipient_ids:
                recipient_agent = crud.get_agent(recipient_db, recipient_id)
                if not recipient_agent:
                    # Log the error
                    logger.warning(f"Recipient agent not found: {recipient_id}")
                    raise HTTPException(
                        status_code=404,
                        detail=f"Recipient agent '{recipient_id}' not found",
                    )

        # Broadcast the message
        messages = await communication_hub.broadcast_message(
            sender_id=message_data.sender_id,
            content=message_data.content,
            recipient_ids=message_data.recipient_ids,
            metadata=message_data.metadata,
        )

        # Log the broadcast
        logger.info(
            f"Message broadcast from {message_data.sender_id} to {len(messages)} recipients"
        )

        return messages
    except HTTPException:
        raise
    except Exception as e:
        # Log the error
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v1/agents/{agent_id}/messages", tags=["Agent Communication"])
async def get_messages(
    agent_id: str,
    other_agent_id: Optional[str] = None,
    limit: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Get messages for an agent.

    Args:
        agent_id: The agent ID.
        other_agent_id: Optional other agent ID to filter messages.
        limit: Optional limit on the number of messages to return.
        db: Database session.

    Returns:
        A list of messages.
    """
    try:
        # Check if the agent exists
        agent = crud.get_agent(db, agent_id)
        if not agent:
            # Log the error
            logger.warning(f"Agent not found for messages: {agent_id}")
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        # If other_agent_id is specified, check if it exists
        if other_agent_id:
            other_agent = crud.get_agent(db, other_agent_id)
            if not other_agent:
                # Log the error
                logger.warning(f"Other agent not found for messages: {other_agent_id}")
                raise HTTPException(
                    status_code=404, detail=f"Agent '{other_agent_id}' not found"
                )

        # Get the messages
        messages = communication_hub.get_message_history(
            agent_id=agent_id,
            other_agent_id=other_agent_id,
            limit=limit,
        )

        # Log the request
        logger.info(
            f"Retrieved {len(messages)} messages for agent {agent_id}"
            + (f" with {other_agent_id}" if other_agent_id else "")
        )

        return messages
    except HTTPException:
        raise
    except Exception as e:
        # Log the error
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/v1/agents/{agent_id}/messages/receive", tags=["Agent Communication"])
async def receive_messages(
    agent_id: str,
    other_agent_id: Optional[str] = None,
    timeout: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """
    Receive messages for an agent.

    Args:
        agent_id: The agent ID.
        other_agent_id: Optional other agent ID to filter messages.
        timeout: Optional timeout in seconds.
        db: Database session.

    Returns:
        A list of messages.
    """
    try:
        # Check if the agent exists
        agent = crud.get_agent(db, agent_id)
        if not agent:
            # Log the error
            logger.warning(f"Agent not found for receiving messages: {agent_id}")
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        # If other_agent_id is specified, check if it exists
        if other_agent_id:
            other_agent = crud.get_agent(db, other_agent_id)
            if not other_agent:
                # Log the error
                logger.warning(
                    f"Other agent not found for receiving messages: {other_agent_id}"
                )
                raise HTTPException(
                    status_code=404, detail=f"Agent '{other_agent_id}' not found"
                )

        # Receive the messages
        messages = await communication_hub.receive_messages(
            agent_id=agent_id,
            other_agent_id=other_agent_id,
            timeout=timeout,
        )

        # Log the request
        logger.info(
            f"Received {len(messages)} messages for agent {agent_id}"
            + (f" from {other_agent_id}" if other_agent_id else "")
        )

        return messages
    except HTTPException:
        raise
    except Exception as e:
        # Log the error
        logger.error(f"Error receiving messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))
