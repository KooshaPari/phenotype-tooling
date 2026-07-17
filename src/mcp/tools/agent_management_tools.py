"""
MCP tools for agent management.

This module provides MCP tools for creating, retrieving, updating, and deleting agents,
as well as for agent communication.
"""

import asyncio
import json
import uuid
import subprocess
import sys
import os
import socket
import aiohttp
import platform
from typing import Dict, List, Optional, Any, Union

from ...services.centralized_agent_manager import centralized_agent_manager
from ...services.agent_communication import communication_hub
from ...utils.logging import logger


def find_available_port(start_port: int = 8006, max_attempts: int = 100) -> int:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return port
        except OSError:
            continue
    raise RuntimeError(
        f"No available port found in range {start_port}-{start_port + max_attempts}"
    )


def get_terminal_command(title: str, command: str) -> List[str]:
    """Get the appropriate terminal command for the current platform."""
    system = platform.system().lower()

    if system == "darwin":  # macOS
        # Use Terminal.app with AppleScript
        script = f"""
        tell application "Terminal"
            do script "{command}"
            set custom title of front window to "{title}"
            activate
        end tell
        """
        return ["osascript", "-e", script]
    elif system == "linux":
        # Try different terminal emulators
        terminals = [
            ["gnome-terminal", "--title", title, "--", "bash", "-c", command],
            ["xterm", "-title", title, "-e", "bash", "-c", command],
            ["konsole", "--title", title, "-e", "bash", "-c", command],
        ]
        for terminal_cmd in terminals:
            try:
                subprocess.run(
                    ["which", terminal_cmd[0]], check=True, capture_output=True
                )
                return terminal_cmd
            except subprocess.CalledProcessError:
                continue
        # Fallback to xterm
        return ["xterm", "-title", title, "-e", "bash", "-c", command]
    else:
        # Windows or other
        return ["cmd", "/c", "start", f'"{title}"', "cmd", "/k", command]


def launch_agent_terminal(
    agent_id: str, agent_name: str, port: int
) -> Optional[subprocess.Popen]:
    """Launch a terminal window for the agent process."""
    try:
        title = f"Agent: {agent_name} ({agent_id}) - Port {port}"

        # Command to run in the terminal - this will show the agent process output
        command = f"""
        echo "=== Agent Terminal: {agent_name} ==="
        echo "Agent ID: {agent_id}"
        echo "Port: {port}"
        echo "Starting agent process..."
        echo ""

        # Source the profile to get Node.js in path
        source /Users/kooshapari/.zprofile 2>/dev/null || true

        # Navigate to the project directory
        cd "$(dirname "$(dirname "$(dirname "$(dirname "$0")")")")" || cd /Users/kooshapari/Downloads/home-2/ubuntu/swe_agent_project/new

        # Run the independent agent with autonomous capabilities
        python run_independent_agent.py --port {port} --agent-id {agent_id} --agent-name "{agent_name}" --model gpt-4o-mini --autonomous --system-prompt "You are {agent_name}, an AI agent running independently. You can communicate with other agents and use MCP tools. Your agent ID is {agent_id}."

        echo ""
        echo "Agent process ended. Press any key to close terminal..."
        read -n 1
        """

        terminal_cmd = get_terminal_command(title, command)

        logger.info(f"Launching terminal for agent {agent_id}: {terminal_cmd}")

        # Launch the terminal
        process = subprocess.Popen(
            terminal_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        return process

    except Exception as e:
        logger.error(f"Failed to launch terminal for agent {agent_id}: {e}")
        return None


async def launch_agent_process(
    agent_id: str,
    name: str,
    model_name: str,
    port: int,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tools: int = 128,
) -> subprocess.Popen:
    """Launch an independent agent process on the specified port."""

    # Get the project root directory (where run_independent_agent.py is located)
    current_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    # Create the command to launch the agent
    cmd = [
        sys.executable,
        os.path.join(current_dir, "run_independent_agent.py"),
        "--port",
        str(port),
        "--agent-id",
        agent_id,
        "--agent-name",
        name,
        "--model",
        model_name,
        "--temperature",
        str(temperature),
        "--max-tools",
        str(max_tools),
    ]

    if system_prompt:
        cmd.extend(["--system-prompt", system_prompt])

    # Set up environment
    env = os.environ.copy()
    env["AGENT_ID"] = agent_id
    env["AGENT_NAME"] = name
    env["AGENT_PORT"] = str(port)

    logger.info(f"Launching agent process: {' '.join(cmd)}")

    # Launch the process
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=current_dir,
    )

    # Give the process a moment to start
    await asyncio.sleep(2)

    return process


async def create_agent_tool(
    name: str,
    model_name: str,
    system_prompt: Optional[str] = None,
    mcp_tools_config_path: Optional[str] = None,
    description: Optional[str] = None,
    temperature: float = 0.7,
    max_tools: Optional[int] = 128,
    launch_process: bool = True,
    role: Optional[str] = None,
    capabilities: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a new agent using the centralized agent manager.

    Args:
        name: The name of the agent.
        model_name: The name of the model to use.
        system_prompt: Optional custom system prompt to use.
        mcp_tools_config_path: Optional path to MCP tools configuration.
        description: Optional description of the agent.
        temperature: The temperature to use for generation.
        max_tools: Maximum number of tools to use.
        launch_process: Whether to launch an independent process for the agent.
        role: The role of the agent (e.g., "Project Manager", "Developer").
        capabilities: List of capabilities the agent has.

    Returns:
        A dictionary containing the agent configuration.
    """
    try:
        # Use the centralized agent manager to create the agent
        result = await centralized_agent_manager.create_agent(
            name=name,
            role=role or "Assistant",
            model_name=model_name,
            description=description,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tools=max_tools,
            capabilities=capabilities or [],
            launch_process=launch_process,
        )

        logger.info(f"Created agent via centralized manager: {result}")
        return result

    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        return {"error": str(e)}


async def create_independent_agent_tool(
    name: str,
    model_name: str,
    system_prompt: Optional[str] = None,
    description: Optional[str] = None,
    temperature: float = 0.7,
    max_tools: int = 128,
) -> Dict[str, Any]:
    """
    Create a new independent agent process with visible terminal.

    Args:
        name: The name of the agent.
        model_name: The name of the model to use.
        system_prompt: Optional custom system prompt to use.
        description: Optional description of the agent.
        temperature: The temperature to use for generation.
        max_tools: Maximum number of tools to use.

    Returns:
        A dictionary containing the agent configuration and process information.
    """
    return await create_agent_tool(
        name=name,
        model_name=model_name,
        system_prompt=system_prompt,
        description=description,
        temperature=temperature,
        max_tools=max_tools,
        launch_process=True,
    )


async def create_swarm_team_tool(
    team_name: str,
    project_description: str,
    team_members: List[Dict[str, str]],
    model_name: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """
    Create a complete swarm team with specialized agents.

    Args:
        team_name: Name of the team.
        project_description: Description of the project they'll work on.
        team_members: List of team member configs with 'name', 'role', and 'expertise'.
        model_name: Model to use for all agents.

    Returns:
        Dictionary with team information and all created agents.
    """
    try:
        created_agents = []

        for member in team_members:
            name = member.get("name")
            role = member.get("role")
            expertise = member.get("expertise", "")

            # Create specialized system prompt
            system_prompt = f"""You are {name}, a {role} working on the {team_name} team.

PROJECT: {project_description}

YOUR ROLE: {role}
YOUR EXPERTISE: {expertise}

TEAM MEMBERS: {', '.join([m.get('name', '') + ' (' + m.get('role', '') + ')' for m in team_members])}

You can communicate with your team members using MCP tools. You should:
1. Provide expertise in your specialized area
2. Collaborate with team members on project planning and execution
3. Respond to messages and task assignments from team members
4. Use your specialized knowledge to contribute to the project

When you receive messages, respond thoughtfully based on your role and expertise.
Always be helpful, professional, and focused on the project goals."""

            # Create the independent agent
            result = await create_independent_agent_tool(
                name=name,
                model_name=model_name,
                system_prompt=system_prompt,
                description=f"{role} for {team_name} team",
                temperature=0.7,
                max_tools=128,
            )

            if "error" not in result:
                created_agents.append(result)
                logger.info(
                    f"Successfully created agent {name} on port {result.get('port')}"
                )
                # Wait longer between agent creation to avoid port conflicts
                await asyncio.sleep(5)
            else:
                logger.error(f"Failed to create agent {name}: {result['error']}")

        return {
            "team_name": team_name,
            "project_description": project_description,
            "agents_created": len(created_agents),
            "agents": created_agents,
            "status": "success" if created_agents else "failed",
        }

    except Exception as e:
        logger.error(f"Error creating swarm team: {e}")
        return {"error": str(e)}


async def invoke_agent_http_tool(
    agent_id: str,
    message: str,
    port: Optional[int] = None,
    uri: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Invoke an agent via HTTP (blocking communication).

    Args:
        agent_id: The agent ID.
        message: The message to send to the agent.
        port: Optional port number if known.
        uri: Optional URI if known.
        temperature: Optional temperature override.
        max_tokens: Optional max tokens override.

    Returns:
        The agent's response.
    """
    try:
        # Get agent information to find the port/URI
        if not uri and not port:
            from ...db.models import get_db

            # Get a database session
            db_gen = get_db()
            db = next(db_gen)

            try:
                agent = await agent_manager.get_agent(agent_id=agent_id, db=db)
                if not agent:
                    return {"error": f"Agent '{agent_id}' not found"}

                port = agent.get("port")
                uri = agent.get("uri")
            finally:
                db.close()

        if not uri:
            if port:
                uri = f"http://localhost:{port}"
            else:
                return {"error": f"No URI or port found for agent '{agent_id}'"}

        # Prepare the request
        request_data = {
            "model": "gpt-4o-mini",  # Default model for the request
            "messages": [{"role": "user", "content": message}],
            "stream": False,
        }

        if temperature is not None:
            request_data["temperature"] = temperature
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens

        # Make the HTTP request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{uri}/v1/chat/completions",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "agent_id": agent_id,
                        "response": result,
                        "status": "success",
                        "uri": uri,
                    }
                else:
                    error_text = await response.text()
                    return {
                        "error": f"HTTP {response.status}: {error_text}",
                        "agent_id": agent_id,
                        "uri": uri,
                    }

    except Exception as e:
        logger.error(f"Error invoking agent via HTTP: {e}")
        return {"error": str(e), "agent_id": agent_id}


async def view_agent_console_tool(agent_id: str) -> Dict[str, Any]:
    """
    Launch a console viewer for an agent to see its output.

    Args:
        agent_id: The agent ID.

    Returns:
        Status of the console viewer launch.
    """
    try:
        # Get agent information
        from ...db.models import get_db

        db_gen = get_db()
        db = next(db_gen)

        try:
            agent = await agent_manager.get_agent(agent_id=agent_id, db=db)
            if not agent:
                return {"error": f"Agent '{agent_id}' not found"}

            agent_name = agent.get("name", "Unknown")
            port = agent.get("port")

            if not port:
                return {
                    "error": f"Agent '{agent_id}' does not have a port assigned (not running as independent process)"
                }

            # Launch a new terminal to monitor the agent
            title = f"Console Viewer: {agent_name} ({agent_id})"

            command = f"""
            echo "=== Agent Console Viewer ==="
            echo "Agent: {agent_name}"
            echo "ID: {agent_id}"
            echo "Port: {port}"
            echo "URI: http://localhost:{port}"
            echo ""
            echo "Monitoring agent process..."
            echo "Press Ctrl+C to exit"
            echo ""

            # Monitor the agent process
            while true; do
                echo "--- $(date) ---"
                if curl -s http://localhost:{port}/health > /dev/null 2>&1; then
                    echo "✅ Agent is responding on port {port}"
                else
                    echo "❌ Agent not responding on port {port}"
                fi
                sleep 5
            done
            """

            terminal_cmd = get_terminal_command(title, command)

            # Launch the console viewer terminal
            process = subprocess.Popen(
                terminal_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            return {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "port": port,
                "console_viewer_launched": True,
                "viewer_process_id": process.pid,
                "status": "success",
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error launching console viewer for agent {agent_id}: {e}")
        return {"error": str(e), "agent_id": agent_id}


async def get_agent_tool(agent_id: str) -> Dict[str, Any]:
    """
    Get an agent by ID.

    Args:
        agent_id: The agent ID.

    Returns:
        A dictionary containing the agent configuration.
    """
    try:
        # Get the agent from centralized manager
        agent = await centralized_agent_manager.get_agent(agent_id)

        if agent is None:
            return {"error": f"Agent '{agent_id}' not found"}

        return agent
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        return {"error": str(e)}


async def list_agents_tool() -> Dict[str, Any]:
    """
    List all agents.

    Returns:
        A dictionary containing a list of agents.
    """
    try:
        # List the agents from centralized manager
        agents = centralized_agent_manager.list_agents()

        return {"agents": agents, "total_count": len(agents)}
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        return {"error": str(e)}


async def update_agent_tool(
    agent_id: str,
    name: Optional[str] = None,
    model_name: Optional[str] = None,
    system_prompt: Optional[str] = None,
    mcp_tools_config_path: Optional[str] = None,
    description: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tools: Optional[int] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an agent.

    Args:
        agent_id: The agent ID.
        name: Optional new name for the agent.
        model_name: Optional new model name for the agent.
        system_prompt: Optional new system prompt for the agent.
        mcp_tools_config_path: Optional new MCP tools configuration path for the agent.
        description: Optional new description for the agent.
        temperature: Optional new temperature for the agent.
        max_tools: Optional new maximum number of tools for the agent.
        status: Optional new status for the agent.

    Returns:
        A dictionary containing the updated agent configuration.
    """
    try:
        # Prepare the update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if model_name is not None:
            update_data["llm_model_id"] = model_name
        if system_prompt is not None:
            update_data["initial_prompt"] = system_prompt
        if mcp_tools_config_path is not None:
            update_data["mcp_tools_config_path"] = mcp_tools_config_path
        if description is not None:
            update_data["description"] = description
        if temperature is not None:
            update_data["temperature"] = temperature
        if max_tools is not None:
            update_data["max_tools"] = max_tools
        if status is not None:
            update_data["status"] = status

        # Update the agent
        agent = await agent_manager.update_agent(
            agent_id=agent_id,
            update_data=update_data,
        )

        if agent is None:
            return {"error": f"Agent '{agent_id}' not found"}

        return {
            "agent_id": agent["agent_id"],
            "name": agent.get("name"),
            "description": agent.get("description"),
            "model_name": agent.get("llm_model_id"),
            "status": agent["status"],
            "in_memory": agent["in_memory"],
        }
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        return {"error": str(e)}


async def delete_agent_tool(agent_id: str) -> Dict[str, Any]:
    """
    Delete/terminate an agent.

    Args:
        agent_id: The agent ID.

    Returns:
        A dictionary indicating success.
    """
    try:
        # Terminate the agent using centralized manager
        result = await centralized_agent_manager.terminate_agent(agent_id)
        return result
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        return {"success": False, "error": str(e)}


async def health_check_agent_tool(agent_id: str) -> Dict[str, Any]:
    """
    Perform health check on an agent.

    Args:
        agent_id: The agent ID.

    Returns:
        Health check results.
    """
    try:
        # Perform health check using centralized manager
        result = await centralized_agent_manager.health_check(agent_id)
        return result
    except Exception as e:
        logger.error(f"Error checking agent health: {e}")
        return {"status": "error", "message": str(e)}


async def invoke_agent_tool(
    agent_id: str,
    message: str,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Invoke an agent via HTTP (blocking communication).

    Args:
        agent_id: The agent ID.
        message: The message to send to the agent.
        temperature: Optional temperature override.
        max_tokens: Optional max tokens override.

    Returns:
        The agent's response.
    """
    try:
        # Use the HTTP invocation method
        return await invoke_agent_http_tool(
            agent_id=agent_id,
            message=message,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as e:
        logger.error(f"Error invoking agent: {e}")
        return {"error": str(e)}


async def send_message_tool(
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
        The sent message.
    """
    try:
        # Send the message
        message = await communication_hub.send_message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            metadata=metadata,
        )

        return message
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {"error": str(e)}


async def broadcast_message_tool(
    sender_id: str,
    content: str,
    recipient_ids: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Broadcast a message to multiple agents.

    Args:
        sender_id: The sender agent ID.
        content: The message content.
        recipient_ids: Optional list of recipient agent IDs.
        metadata: Optional message metadata.

    Returns:
        The sent messages.
    """
    try:
        # Broadcast the message
        messages = await communication_hub.broadcast_message(
            sender_id=sender_id,
            content=content,
            recipient_ids=recipient_ids,
            metadata=metadata,
        )

        return {"messages": messages}
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        return {"error": str(e)}


async def get_messages_tool(
    agent_id: str,
    other_agent_id: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get messages for an agent.

    Args:
        agent_id: The agent ID.
        other_agent_id: Optional other agent ID to filter messages.
        limit: Optional limit on the number of messages to return.

    Returns:
        A list of messages.
    """
    try:
        # Get the messages
        messages = communication_hub.get_message_history(
            agent_id=agent_id,
            other_agent_id=other_agent_id,
            limit=limit,
        )

        return {"messages": messages}
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return {"error": str(e)}


async def receive_messages_tool(
    agent_id: str,
    other_agent_id: Optional[str] = None,
    timeout: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Receive messages for an agent.

    Args:
        agent_id: The agent ID.
        other_agent_id: Optional other agent ID to filter messages.
        timeout: Optional timeout in seconds.

    Returns:
        A list of messages.
    """
    try:
        # Receive the messages
        messages = await communication_hub.receive_messages(
            agent_id=agent_id,
            other_agent_id=other_agent_id,
            timeout=timeout,
        )

        return {"messages": messages}
    except Exception as e:
        logger.error(f"Error receiving messages: {e}")
        return {"error": str(e)}
