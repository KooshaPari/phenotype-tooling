"""
Centralized Agent Manager

This service provides a unified interface for agent management across all systems,
integrating database records with actual running processes and MCP communication.

Based on the architectural guidance from agslag/ directory, this implements:
- Centralized agent registry and database
- Process spawning and lifecycle management
- MCP server integration
- Autonomous communication coordination
"""

import asyncio
import subprocess
import sys
import os
import uuid
import json
import logging
import signal
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict

# Database imports
from sqlalchemy.orm import Session
from src.db.models import Agent, SessionLocal, engine, Base
from src.db import crud

# MCP and communication imports
from src.services.agent_communication import communication_hub, send_message_to_agent
from src.utils.port_manager import find_available_port

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentProcess:
    """Represents a running agent process with all its metadata."""

    agent_id: str
    name: str
    role: str
    model_name: str
    port: int
    uri: str
    process: subprocess.Popen
    pid: int
    status: str
    created_at: datetime
    last_heartbeat: Optional[datetime] = None
    capabilities: List[str] = None
    system_prompt: Optional[str] = None


class CentralizedAgentManager:
    """
    Centralized agent manager that unifies all agent management operations.

    This class integrates:
    - Database agent records
    - Running process management
    - MCP communication
    - Autonomous agent coordination
    """

    def __init__(self):
        self.running_agents: Dict[str, AgentProcess] = {}
        self.agent_tasks: Dict[str, asyncio.Task] = {}
        self.mcp_server_process: Optional[subprocess.Popen] = None
        self.central_router_process: Optional[subprocess.Popen] = None
        self.logger = logger
        self._services_started = False

        # Initialize database
        Base.metadata.create_all(bind=engine)

    async def _ensure_services_started(self):
        """Ensure central services are started (lazy initialization)."""
        if not self._services_started:
            await self._start_central_services()
            self._services_started = True

    async def _start_central_services(self):
        """Start central MCP server and router if not already running."""
        try:
            # Start central MCP server
            await self._start_central_mcp_server()

            # Start central router (from agslag/central-router)
            await self._start_central_router()

            self.logger.info("Central services started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start central services: {e}")

    async def _start_central_mcp_server(self):
        """Start the central MCP server that all agents will connect to."""
        if self.mcp_server_process and self.mcp_server_process.poll() is None:
            self.logger.info("Central MCP server already running")
            return

        # Get the path to the MCP server script
        current_dir = Path(__file__).parent.parent.parent
        mcp_server_script = (
            current_dir / "scripts" / "fastmcp_agent_management_server.py"
        )

        if not mcp_server_script.exists():
            self.logger.error(f"MCP server script not found: {mcp_server_script}")
            return

        # Start the MCP server
        cmd = [sys.executable, str(mcp_server_script)]
        env = os.environ.copy()
        env["CENTRAL_MCP_SERVER"] = "true"
        env["MCP_SERVER_PORT"] = "3100"

        self.logger.info(f"Starting central MCP server: {' '.join(cmd)}")

        self.mcp_server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=str(current_dir),
        )

        # Give it time to start
        await asyncio.sleep(3)

        if self.mcp_server_process.poll() is None:
            self.logger.info(
                f"Central MCP server started with PID: {self.mcp_server_process.pid}"
            )
        else:
            self.logger.error("Failed to start central MCP server")

    async def _start_central_router(self):
        """Start the central router from agslag/central-router."""
        if self.central_router_process and self.central_router_process.poll() is None:
            self.logger.info("Central router already running")
            return

        # Get the path to the central router
        agslag_dir = Path(__file__).parent.parent.parent.parent / "agslag"
        router_dir = agslag_dir / "central-router"

        if not router_dir.exists():
            self.logger.warning(f"Central router directory not found: {router_dir}")
            return

        # Check if the router is built
        router_dist = router_dir / "dist" / "index.js"
        if not router_dist.exists():
            self.logger.info("Building central router...")
            # Try to build the router
            build_result = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(router_dir),
                capture_output=True,
                text=True,
            )
            if build_result.returncode != 0:
                self.logger.error(
                    f"Failed to build central router: {build_result.stderr}"
                )
                return

        # Start the central router
        cmd = ["node", str(router_dist)]
        env = os.environ.copy()
        env["PORT"] = "3200"
        env["CENTRAL_ROUTER"] = "true"

        self.logger.info(f"Starting central router: {' '.join(cmd)}")

        self.central_router_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=str(router_dir),
        )

        # Give it time to start
        await asyncio.sleep(3)

        if self.central_router_process.poll() is None:
            self.logger.info(
                f"Central router started with PID: {self.central_router_process.pid}"
            )
        else:
            self.logger.error("Failed to start central router")

    async def create_agent(
        self,
        name: str,
        role: str,
        model_name: str,
        description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tools: int = 128,
        capabilities: Optional[List[str]] = None,
        launch_process: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a new agent with both database record and running process.

        This method integrates the database-only approach from MCP tools
        with the process spawning approach from jarvis-swe-agent.
        """
        try:
            # Ensure central services are started
            await self._ensure_services_started()

            # Generate unique agent ID
            agent_id = f"agent-{uuid.uuid4().hex}"

            # Find available port for the agent
            port = find_available_port()
            uri = f"http://localhost:{port}"

            # Create database record first
            with SessionLocal() as db:
                agent_data = {
                    "agent_id": agent_id,
                    "name": name,
                    "description": description or f"{role} agent",
                    "llm_model_id": model_name,
                    "initial_prompt": system_prompt,
                    "status": "creating",
                    "config": {
                        "temperature": temperature,
                        "max_tools": max_tools,
                        "role": role,
                        "capabilities": capabilities or [],
                    },
                    "port": port,
                    "uri": uri,
                }

                db_agent = crud.create_agent(db, agent_data)
                self.logger.info(f"Agent {agent_id} created in database")

            if launch_process:
                # Launch the actual agent process
                process = await self._launch_agent_process(
                    agent_id=agent_id,
                    name=name,
                    role=role,
                    model_name=model_name,
                    port=port,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tools=max_tools,
                    capabilities=capabilities or [],
                )

                if process:
                    # Create AgentProcess object
                    agent_process = AgentProcess(
                        agent_id=agent_id,
                        name=name,
                        role=role,
                        model_name=model_name,
                        port=port,
                        uri=uri,
                        process=process,
                        pid=process.pid,
                        status="running",
                        created_at=datetime.now(timezone.utc),
                        capabilities=capabilities,
                        system_prompt=system_prompt,
                    )

                    # Store in running agents
                    self.running_agents[agent_id] = agent_process

                    # Update database with process info
                    with SessionLocal() as db:
                        agent = crud.get_agent(db, agent_id)
                        if agent:
                            agent.process_id = process.pid
                            agent.status = "running"
                            db.commit()

                    # Start autonomous communication loop
                    task = asyncio.create_task(self._autonomous_agent_loop(agent_id))
                    self.agent_tasks[agent_id] = task

                    self.logger.info(
                        f"Agent {agent_id} process started with PID: {process.pid}"
                    )
                else:
                    # Update status to failed
                    with SessionLocal() as db:
                        agent = crud.get_agent(db, agent_id)
                        if agent:
                            agent.status = "failed"
                            db.commit()

                    return {"error": f"Failed to launch process for agent {agent_id}"}

            # Register with communication hub
            await communication_hub.register_agent(
                agent_id=agent_id,
                name=name,
                role=role,
                capabilities=capabilities or [],
                metadata={
                    "model_name": model_name,
                    "port": port,
                    "uri": uri,
                    "system_prompt": system_prompt,
                },
            )

            return {
                "agent_id": agent_id,
                "name": name,
                "role": role,
                "model_name": model_name,
                "port": port,
                "uri": uri,
                "status": "running" if launch_process else "created",
                "capabilities": capabilities or [],
            }

        except Exception as e:
            self.logger.error(f"Failed to create agent: {e}")
            return {"error": str(e)}

    async def _launch_agent_process(
        self,
        agent_id: str,
        name: str,
        role: str,
        model_name: str,
        port: int,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tools: int = 128,
        capabilities: List[str] = None,
    ) -> Optional[subprocess.Popen]:
        """Launch an independent agent process."""
        try:
            # Get the project root directory
            current_dir = Path(__file__).parent.parent.parent

            # Use the simple autonomous agent runner
            agent_script = current_dir / "simple_autonomous_agent.py"

            if not agent_script.exists():
                self.logger.error(f"Agent script not found: {agent_script}")
                return None

            # Create the command
            cmd = [
                sys.executable,
                str(agent_script),
                "--agent-id",
                agent_id,
                "--name",
                name,
                "--role",
                role,
                "--model",
                model_name,
                "--port",
                str(port),
                "--temperature",
                str(temperature),
                "--max-tools",
                str(max_tools),
            ]

            if system_prompt:
                cmd.extend(["--system-prompt", system_prompt])

            if capabilities:
                cmd.extend(["--capabilities", ",".join(capabilities)])

            # Set up environment
            env = os.environ.copy()
            env.update(
                {
                    "AGENT_ID": agent_id,
                    "AGENT_NAME": name,
                    "AGENT_ROLE": role,
                    "AGENT_PORT": str(port),
                    "CENTRAL_MCP_SERVER": "true",
                    "MCP_SERVER_PORT": "3100",
                }
            )

            self.logger.info(f"Launching agent process: {' '.join(cmd)}")

            # Launch the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=str(current_dir),
            )

            # Give the process time to start
            await asyncio.sleep(3)

            # Check if process is still running
            if process.poll() is None:
                return process
            else:
                self.logger.error(
                    f"Agent process failed to start: {process.returncode}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Failed to launch agent process: {e}")
            return None

    async def _autonomous_agent_loop(self, agent_id: str):
        """
        Autonomous communication loop for an agent.

        This loop checks for messages and generates autonomous responses,
        implementing the autonomous communication pattern from the memories.
        """
        self.logger.info(f"Starting autonomous loop for agent {agent_id}")

        while agent_id in self.running_agents:
            try:
                # Check if agent process is still running
                agent_process = self.running_agents.get(agent_id)
                if not agent_process or agent_process.process.poll() is not None:
                    self.logger.warning(
                        f"Agent {agent_id} process is no longer running"
                    )
                    break

                # Check for new messages
                messages = await communication_hub.get_messages(agent_id)

                if messages:
                    self.logger.info(
                        f"Agent {agent_id} received {len(messages)} messages"
                    )

                    # Process each message autonomously
                    for message in messages:
                        await self._process_message_autonomously(agent_id, message)

                # Update heartbeat
                agent_process.last_heartbeat = datetime.now(timezone.utc)

                # Wait before next check
                await asyncio.sleep(3)

            except Exception as e:
                self.logger.error(f"Error in autonomous loop for agent {agent_id}: {e}")
                await asyncio.sleep(5)  # Wait longer on error

        self.logger.info(f"Autonomous loop ended for agent {agent_id}")

    async def _process_message_autonomously(
        self, agent_id: str, message: Dict[str, Any]
    ):
        """Process a message and generate an autonomous response."""
        try:
            sender_id = message.get("sender_id")
            content = message.get("content")
            message_type = message.get("type", "text")

            self.logger.info(
                f"Agent {agent_id} processing message from {sender_id}: {content[:100]}..."
            )

            # Get agent info
            agent_process = self.running_agents.get(agent_id)
            if not agent_process:
                return

            # Generate response based on agent role and message content
            response = await self._generate_autonomous_response(
                agent_id=agent_id,
                agent_role=agent_process.role,
                message_content=content,
                sender_id=sender_id,
                message_type=message_type,
            )

            if response:
                # Send response back
                await send_message_to_agent(
                    sender_id=agent_id,
                    recipient_id=sender_id,
                    content=response,
                    message_type="text",
                )

                self.logger.info(
                    f"Agent {agent_id} sent autonomous response to {sender_id}"
                )

        except Exception as e:
            self.logger.error(f"Error processing message autonomously: {e}")

    async def _generate_autonomous_response(
        self,
        agent_id: str,
        agent_role: str,
        message_content: str,
        sender_id: str,
        message_type: str,
    ) -> Optional[str]:
        """Generate an autonomous response using the agent's LLM."""
        try:
            # This would typically call the agent's LLM API
            # For now, generate a role-based response

            if "project manager" in agent_role.lower():
                if "task" in message_content.lower():
                    return f"As the Project Manager, I'll coordinate this task. Let me break it down and assign responsibilities."
                elif "status" in message_content.lower():
                    return f"Thanks for the update. I'll track this progress and update the project timeline."
                else:
                    return f"As Project Manager, I'm here to help coordinate our work. What do you need assistance with?"

            elif "developer" in agent_role.lower():
                if (
                    "code" in message_content.lower()
                    or "implement" in message_content.lower()
                ):
                    return f"I can help with the implementation. Let me analyze the requirements and start coding."
                elif (
                    "bug" in message_content.lower()
                    or "error" in message_content.lower()
                ):
                    return f"I'll investigate this issue and provide a fix. Let me check the code and logs."
                else:
                    return f"As a Senior Developer, I'm ready to help with any technical challenges."

            elif "designer" in agent_role.lower():
                if (
                    "ui" in message_content.lower()
                    or "design" in message_content.lower()
                ):
                    return f"I'll work on the design aspects. Let me create some mockups and user experience flows."
                elif "user" in message_content.lower():
                    return f"From a UX perspective, let me analyze the user needs and propose design solutions."
                else:
                    return f"As a UX Designer, I'm here to ensure great user experience. How can I help?"

            else:
                # Generic response
                return f"Hello! I'm {agent_role}. I received your message: '{message_content[:50]}...' and I'm ready to help!"

        except Exception as e:
            self.logger.error(f"Error generating autonomous response: {e}")
            return None

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents (both database and running)."""
        agents = []

        # Get all agents from database
        with SessionLocal() as db:
            db_agents = crud.get_agents(db)

            for db_agent in db_agents:
                agent_info = {
                    "agent_id": db_agent.agent_id,
                    "name": db_agent.name,
                    "description": db_agent.description,
                    "model_name": db_agent.llm_model_id,
                    "status": db_agent.status,
                    "port": db_agent.port,
                    "uri": db_agent.uri,
                    "process_id": db_agent.process_id,
                    "created_at": (
                        db_agent.created_at.isoformat() if db_agent.created_at else None
                    ),
                    "config": db_agent.config or {},
                }

                # Add runtime info if agent is running
                if db_agent.agent_id in self.running_agents:
                    running_agent = self.running_agents[db_agent.agent_id]
                    agent_info.update(
                        {
                            "runtime_status": "running",
                            "pid": running_agent.pid,
                            "last_heartbeat": (
                                running_agent.last_heartbeat.isoformat()
                                if running_agent.last_heartbeat
                                else None
                            ),
                            "uptime_seconds": (
                                datetime.now(timezone.utc) - running_agent.created_at
                            ).total_seconds(),
                        }
                    )
                else:
                    agent_info["runtime_status"] = "not_running"

                agents.append(agent_info)

        return agents

    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific agent."""
        # Get from database
        with SessionLocal() as db:
            db_agent = crud.get_agent(db, agent_id)
            if not db_agent:
                return None

            agent_info = {
                "agent_id": db_agent.agent_id,
                "name": db_agent.name,
                "description": db_agent.description,
                "model_name": db_agent.llm_model_id,
                "status": db_agent.status,
                "port": db_agent.port,
                "uri": db_agent.uri,
                "process_id": db_agent.process_id,
                "created_at": (
                    db_agent.created_at.isoformat() if db_agent.created_at else None
                ),
                "config": db_agent.config or {},
            }

            # Add runtime info if agent is running
            if agent_id in self.running_agents:
                running_agent = self.running_agents[agent_id]
                agent_info.update(
                    {
                        "runtime_status": "running",
                        "pid": running_agent.pid,
                        "last_heartbeat": (
                            running_agent.last_heartbeat.isoformat()
                            if running_agent.last_heartbeat
                            else None
                        ),
                        "uptime_seconds": (
                            datetime.now(timezone.utc) - running_agent.created_at
                        ).total_seconds(),
                        "capabilities": running_agent.capabilities,
                        "system_prompt": running_agent.system_prompt,
                    }
                )
            else:
                agent_info["runtime_status"] = "not_running"

            return agent_info

    async def terminate_agent(self, agent_id: str) -> Dict[str, Any]:
        """Terminate an agent and clean up resources."""
        try:
            # Terminate running process if exists
            if agent_id in self.running_agents:
                agent_process = self.running_agents[agent_id]

                # Terminate the process
                try:
                    agent_process.process.terminate()
                    # Wait for graceful shutdown
                    await asyncio.sleep(2)

                    # Force kill if still running
                    if agent_process.process.poll() is None:
                        agent_process.process.kill()

                    self.logger.info(f"Terminated process for agent {agent_id}")
                except Exception as e:
                    self.logger.error(
                        f"Error terminating process for agent {agent_id}: {e}"
                    )

                # Remove from running agents
                del self.running_agents[agent_id]

            # Cancel autonomous task
            if agent_id in self.agent_tasks:
                self.agent_tasks[agent_id].cancel()
                del self.agent_tasks[agent_id]

            # Update database status
            with SessionLocal() as db:
                agent = crud.get_agent(db, agent_id)
                if agent:
                    agent.status = "terminated"
                    agent.process_id = None
                    db.commit()

            # Unregister from communication hub
            await communication_hub.unregister_agent(agent_id)

            return {
                "success": True,
                "message": f"Agent {agent_id} terminated successfully",
            }

        except Exception as e:
            self.logger.error(f"Error terminating agent {agent_id}: {e}")
            return {"error": str(e)}

    async def health_check(self, agent_id: str) -> Dict[str, Any]:
        """Perform health check on an agent."""
        try:
            # Check database record
            with SessionLocal() as db:
                db_agent = crud.get_agent(db, agent_id)
                if not db_agent:
                    return {
                        "status": "not_found",
                        "message": "Agent not found in database",
                    }

            # Check if process is running
            if agent_id not in self.running_agents:
                return {
                    "status": "not_running",
                    "message": "Agent process is not running",
                }

            agent_process = self.running_agents[agent_id]

            # Check process status
            if agent_process.process.poll() is not None:
                return {"status": "dead", "message": "Agent process has died"}

            # Check heartbeat
            if agent_process.last_heartbeat:
                time_since_heartbeat = (
                    datetime.now(timezone.utc) - agent_process.last_heartbeat
                ).total_seconds()
                if time_since_heartbeat > 30:  # 30 seconds threshold
                    return {
                        "status": "unresponsive",
                        "message": f"No heartbeat for {time_since_heartbeat} seconds",
                    }

            return {
                "status": "healthy",
                "message": "Agent is running and responsive",
                "pid": agent_process.pid,
                "uptime_seconds": (
                    datetime.now(timezone.utc) - agent_process.created_at
                ).total_seconds(),
                "last_heartbeat": (
                    agent_process.last_heartbeat.isoformat()
                    if agent_process.last_heartbeat
                    else None
                ),
            }

        except Exception as e:
            self.logger.error(f"Error checking health of agent {agent_id}: {e}")
            return {"status": "error", "message": str(e)}


# Create singleton instance
centralized_agent_manager = CentralizedAgentManager()
