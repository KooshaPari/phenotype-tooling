"""
Agent Manager Service for managing agent lifecycle.

This service provides functionality for creating, retrieving, updating, and deleting agents.
It also supports injecting custom prompts during agent creation and manages agent communication.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging

from sqlalchemy.orm import Session

from ..agent import SWEAgent
from ..db import crud
from ..db.models import get_db
from ..mcp.client import load_mcp_config
from ..utils.logging import logger


class AgentManager:
    """
    Service for managing agent lifecycle and communication.
    """

    def __init__(self):
        """Initialize the agent manager."""
        self.agents: Dict[str, SWEAgent] = {}
        self.agent_tasks: Dict[str, asyncio.Task] = {}
        self.logger = logger

    async def create_agent(
        self,
        name: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        mcp_tools_config_path: Optional[str] = None,
        description: Optional[str] = None,
        temperature: float = 0.7,
        max_tools: Optional[int] = 128,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Create a new agent with the specified parameters.

        Args:
            name: The name of the agent.
            model_name: The name of the model to use.
            system_prompt: Optional custom system prompt to use.
            mcp_tools_config_path: Optional path to MCP tools configuration.
            description: Optional description of the agent.
            temperature: The temperature to use for generation.
            max_tools: Maximum number of tools to use.
            db: Optional database session.

        Returns:
            A dictionary containing the agent configuration.
        """
        # Generate a unique ID for the agent
        agent_id = f"agent-{uuid.uuid4().hex}"

        # Create the agent config
        agent_config = {
            "agent_id": agent_id,
            "name": name,
            "description": description,
            "llm_model_id": model_name,
            "mcp_tools_config_path": mcp_tools_config_path,
            "initial_prompt": system_prompt,
            "status": "creating",
            "config": {
                "temperature": temperature,
                "max_tools": max_tools,
            },
        }

        # Create the agent in the database if a session is provided
        if db:
            db_agent = crud.create_agent(db, agent_config)
            self.logger.info(f"Agent created in database: {agent_id}")

        # Create and initialize the agent
        try:
            agent = SWEAgent(
                model_name=model_name,
                temperature=temperature,
                system_prompt=system_prompt,
                max_tools=max_tools,
            )

            # Store the agent instance
            self.agents[agent_id] = agent

            # Initialize the agent in a background task
            task = asyncio.create_task(self._initialize_agent(agent_id, agent, db))
            self.agent_tasks[agent_id] = task

            self.logger.info(f"Agent creation started: {agent_id}")

            return {
                "agent_id": agent_id,
                "name": name,
                "description": description,
                "llm_model_id": model_name,
                "mcp_tools_config_path": mcp_tools_config_path,
                "initial_prompt": system_prompt,
                "status": "creating",
            }
        except Exception as e:
            self.logger.error(f"Error creating agent: {e}")
            if agent_id in self.agents:
                del self.agents[agent_id]
            if db:
                agent_update = {"status": "error"}
                crud.update_agent(db, agent_id, agent_update)
            raise

    async def _initialize_agent(
        self, agent_id: str, agent: SWEAgent, db: Optional[Session] = None
    ):
        """
        Initialize an agent in the background.

        Args:
            agent_id: The agent ID.
            agent: The agent instance.
            db: Optional database session.
        """
        try:
            # Initialize the agent
            await agent.initialize()

            # Update the agent status
            if db:
                agent_update = {"status": "active"}
                crud.update_agent(db, agent_id, agent_update)

            self.logger.info(f"Agent initialized successfully: {agent_id}")
        except Exception as e:
            self.logger.error(f"Error initializing agent {agent_id}: {e}")
            if db:
                agent_update = {"status": "error"}
                crud.update_agent(db, agent_id, agent_update)

    async def get_agent(
        self, agent_id: str, db: Optional[Session] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get an agent by ID.

        Args:
            agent_id: The agent ID.
            db: Optional database session.

        Returns:
            A dictionary containing the agent configuration, or None if not found.
        """
        # Check if the agent exists in memory
        if agent_id in self.agents:
            # If a database session is provided, get the agent from the database
            if db:
                db_agent = crud.get_agent(db, agent_id)
                if db_agent:
                    return {
                        "agent_id": db_agent.agent_id,
                        "name": db_agent.name,
                        "description": db_agent.description,
                        "llm_model_id": db_agent.llm_model_id,
                        "mcp_tools_config_path": db_agent.mcp_tools_config_path,
                        "initial_prompt": db_agent.initial_prompt,
                        "status": db_agent.status,
                        "port": db_agent.port,
                        "uri": db_agent.uri,
                        "process_id": db_agent.process_id,
                        "in_memory": True,
                    }

            # If no database session is provided or the agent is not in the database,
            # return a basic configuration
            return {
                "agent_id": agent_id,
                "status": "active" if agent_id in self.agents else "unknown",
                "in_memory": True,
            }

        # If the agent is not in memory, check the database
        if db:
            db_agent = crud.get_agent(db, agent_id)
            if db_agent:
                return {
                    "agent_id": db_agent.agent_id,
                    "name": db_agent.name,
                    "description": db_agent.description,
                    "llm_model_id": db_agent.llm_model_id,
                    "mcp_tools_config_path": db_agent.mcp_tools_config_path,
                    "initial_prompt": db_agent.initial_prompt,
                    "status": db_agent.status,
                    "port": db_agent.port,
                    "uri": db_agent.uri,
                    "process_id": db_agent.process_id,
                    "in_memory": False,
                }

        return None

    async def list_agents(self, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        """
        List all agents.

        Args:
            db: Optional database session.

        Returns:
            A list of dictionaries containing agent configurations.
        """
        agents = []

        # If a database session is provided, get all agents from the database
        if db:
            db_agents = crud.get_agents(db)
            for db_agent in db_agents:
                agents.append(
                    {
                        "agent_id": db_agent.agent_id,
                        "name": db_agent.name,
                        "description": db_agent.description,
                        "llm_model_id": db_agent.llm_model_id,
                        "mcp_tools_config_path": db_agent.mcp_tools_config_path,
                        "initial_prompt": db_agent.initial_prompt,
                        "status": db_agent.status,
                        "port": db_agent.port,
                        "uri": db_agent.uri,
                        "process_id": db_agent.process_id,
                        "in_memory": db_agent.agent_id in self.agents,
                    }
                )
        else:
            # If no database session is provided, return only in-memory agents
            for agent_id in self.agents:
                agents.append(
                    {
                        "agent_id": agent_id,
                        "status": "active",
                        "in_memory": True,
                    }
                )

        return agents

    async def update_agent(
        self,
        agent_id: str,
        update_data: Dict[str, Any],
        db: Optional[Session] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update an agent.

        Args:
            agent_id: The agent ID.
            update_data: The data to update.
            db: Optional database session.

        Returns:
            A dictionary containing the updated agent configuration, or None if not found.
        """
        # Check if the agent exists
        if agent_id not in self.agents and (not db or not crud.get_agent(db, agent_id)):
            return None

        # Update the agent in the database if a session is provided
        if db:
            updated_db_agent = crud.update_agent(db, agent_id, update_data)
            if not updated_db_agent:
                return None

        # Check if we need to reinitialize the agent
        reinitialize = False
        if agent_id in self.agents and any(
            key in update_data
            for key in ["llm_model_id", "initial_prompt", "mcp_tools_config_path"]
        ):
            reinitialize = True

            # Update the agent instance
            agent = self.agents[agent_id]
            if "llm_model_id" in update_data:
                agent.model_name = update_data["llm_model_id"]
            if "initial_prompt" in update_data:
                agent.system_prompt = update_data["initial_prompt"]

            # Reinitialize the agent
            if reinitialize:
                # Cancel any existing initialization task
                if agent_id in self.agent_tasks:
                    self.agent_tasks[agent_id].cancel()

                # Initialize the agent in a background task
                task = asyncio.create_task(self._initialize_agent(agent_id, agent, db))
                self.agent_tasks[agent_id] = task

        # Get the updated agent configuration
        return await self.get_agent(agent_id, db)

    async def delete_agent(self, agent_id: str, db: Optional[Session] = None) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: The agent ID.
            db: Optional database session.

        Returns:
            True if the agent was deleted, False otherwise.
        """
        # Delete the agent from the database if a session is provided
        if db:
            success = crud.delete_agent(db, agent_id)
            if not success:
                return False

        # Delete the agent from memory
        if agent_id in self.agents:
            # Cancel any existing initialization task
            if agent_id in self.agent_tasks:
                self.agent_tasks[agent_id].cancel()
                del self.agent_tasks[agent_id]

            # Delete the agent
            del self.agents[agent_id]

            return True

        return db is not None  # Return True if the agent was deleted from the database

    async def invoke_agent(
        self,
        agent_id: str,
        messages: List[Dict[str, Any]],
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Any:
        """
        Invoke an agent with a set of messages.

        Args:
            agent_id: The agent ID.
            messages: The messages to send to the agent.
            stream: Whether to stream the response.
            temperature: Optional temperature override.
            max_tokens: Optional max tokens override.

        Returns:
            The agent's response.
        """
        # Check if the agent exists
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' not found")

        # Get the agent
        agent = self.agents[agent_id]

        # Prepare the agent input
        agent_input = {
            "messages": messages,
            "agent_config": {
                "temperature": (
                    temperature if temperature is not None else agent.temperature
                ),
                "max_tokens": max_tokens,
                "agent_id": agent_id,
                "request_id": f"req-{uuid.uuid4().hex}",
            },
        }

        # Invoke the agent
        if stream:
            return agent.stream(agent_input)
        else:
            return await agent.invoke(agent_input)


# Create a singleton instance
agent_manager = AgentManager()
