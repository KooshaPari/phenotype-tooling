#!/usr/bin/env python3
"""
Agent Manager TUI - Terminal User Interface for agent management.

This module provides a TUI for monitoring and managing agents, displaying
their status, port, and URI information.
"""

import os
import sys
import time
import logging
import curses
import subprocess
from enum import Enum

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agent registry
from agent_registry import get_registry

# Import agent logger
try:
    from agent_logger import launch_log_viewer

    HAS_LOG_VIEWER = True
except ImportError:
    HAS_LOG_VIEWER = False
    logging.warning("Agent logger not available, console viewing disabled")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="agent_manager_tui.log",
)
logger = logging.getLogger("agent-manager-tui")


# Agent status enum
class AgentStatus(str, Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    INACTIVE = "inactive"
    TERMINATED = "terminated"


# Status symbols - using ASCII characters to avoid encoding issues
STATUS_SYMBOLS = {
    AgentStatus.INITIALIZING: "?",
    AgentStatus.ACTIVE: "+",
    AgentStatus.BUSY: "*",
    AgentStatus.ERROR: "X",
    AgentStatus.INACTIVE: "!",
    AgentStatus.TERMINATED: "X",
}

# Status colors
STATUS_COLORS = {
    AgentStatus.INITIALIZING: 3,  # Yellow
    AgentStatus.ACTIVE: 2,  # Green
    AgentStatus.BUSY: 6,  # Cyan
    AgentStatus.ERROR: 1,  # Red
    AgentStatus.INACTIVE: 4,  # Blue
    AgentStatus.TERMINATED: 1,  # Red
}


class AgentManagerTUI:
    """Terminal User Interface for agent management."""

    def __init__(self, registry):
        """Initialize the TUI.

        Args:
            registry: The agent registry instance
        """
        self.registry = registry
        self.agents = []
        self.selected_index = 0
        self.running = True
        self.update_interval = 2  # seconds
        self.last_update = 0
        self.screen = None
        self.max_y = 0
        self.max_x = 0

    def start(self):
        """Start the TUI."""
        curses.wrapper(self.main)

    def main(self, stdscr):
        """Main TUI function.

        Args:
            stdscr: The curses standard screen
        """
        self.screen = stdscr

        # Set up colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, 8):
            curses.init_pair(i, i, -1)

        # Hide cursor
        curses.curs_set(0)

        # Enable keypad
        stdscr.keypad(True)

        # Set non-blocking input
        stdscr.nodelay(True)

        # Main loop
        while self.running:
            # Get screen dimensions
            self.max_y, self.max_x = stdscr.getmaxyx()

            # Handle input
            self.handle_input()

            # Update agents list
            self.update_agents()

            # Draw UI
            self.draw_ui()

            # Sleep
            time.sleep(0.1)

    def handle_input(self):
        """Handle user input."""
        try:
            key = self.screen.getch()

            if key == curses.KEY_UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif key == curses.KEY_DOWN:
                self.selected_index = min(len(self.agents) - 1, self.selected_index + 1)
            elif key == ord("q"):
                self.running = False
            elif key == ord("r"):
                # Force refresh
                self.last_update = 0
            elif key == ord("d"):
                # Delete selected agent
                if self.agents and 0 <= self.selected_index < len(self.agents):
                    agent_id = self.agents[self.selected_index]["agent_id"]
                    self.registry.delete_agent(agent_id)
                    self.last_update = 0
            elif key == ord("c") or key == ord("v"):
                # Launch console viewer for selected agent
                if (
                    HAS_LOG_VIEWER
                    and self.agents
                    and 0 <= self.selected_index < len(self.agents)
                ):
                    agent_id = self.agents[self.selected_index]["agent_id"]
                    agent_name = self.agents[self.selected_index].get(
                        "name", "Unknown Agent"
                    )

                    try:
                        # Launch log viewer
                        success = launch_log_viewer(agent_id, agent_name)
                        if success:
                            # Show a brief message
                            self.show_message(
                                f"Console viewer launched for {agent_name}"
                            )
                        else:
                            self.show_message("Failed to launch console viewer")
                    except Exception as e:
                        logger.error(f"Error launching console viewer: {e}")
                        self.show_message(f"Error: {str(e)}")
        except Exception as e:
            logger.error(f"Error handling input: {e}")

    def show_message(self, message, duration=1.0):
        """Show a temporary message at the bottom of the screen.

        Args:
            message: The message to show
            duration: How long to show the message in seconds
        """
        try:
            # Save current cursor position
            y, x = self.screen.getyx()

            # Calculate position for message (centered on bottom line)
            msg_y = self.max_y - 1
            msg_x = max(1, (self.max_x - len(message)) // 2)

            # Display message
            self.screen.addnstr(
                msg_y,
                msg_x,
                message,
                min(len(message), self.max_x - msg_x - 1),
                curses.A_BOLD | curses.A_REVERSE,
            )
            self.screen.refresh()

            # Wait for specified duration
            time.sleep(duration)

            # Restore screen
            self.draw_ui()

            # Restore cursor position
            self.screen.move(y, x)
        except Exception as e:
            logger.error(f"Error showing message: {e}")

    def update_agents(self):
        """Update the agents list from the registry."""
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            try:
                agents = self.registry.list_agents()
                # Ensure agents is always a list, even if None is returned
                self.agents = agents if agents is not None else []
                self.last_update = current_time
            except Exception as e:
                logger.error(f"Error updating agents: {e}")
                # Set to empty list on error
                self.agents = []

    def draw_ui(self):
        """Draw the user interface."""
        try:
            self.screen.clear()

            # Draw title - ensure it fits within screen bounds
            title = "Agent Management System"
            if self.max_x > 2:  # Make sure we have at least some space
                try:
                    # Calculate safe title length and position
                    title_length = min(len(title), self.max_x - 2)
                    title_pos = max(
                        0,
                        min(
                            (self.max_x - title_length) // 2,
                            self.max_x - title_length - 1,
                        ),
                    )

                    # Use addnstr for safer string display
                    self.screen.addnstr(
                        0, title_pos, title, title_length, curses.A_BOLD
                    )
                except curses.error:
                    # If still failing, try with a minimal title at position 0
                    try:
                        self.screen.addnstr(0, 0, "Agents", 6, curses.A_BOLD)
                    except curses.error:
                        pass

            # Draw header - ensure it fits within screen bounds
            header = "Status | Agent ID                             | Name                 | Model          | Port  | URI"
            if self.max_y > 2 and self.max_x > 2:  # Make sure we have enough lines
                # Calculate safe header length
                header_length = min(len(header), self.max_x - 2)

                try:
                    # Use addnstr for safer string display
                    self.screen.addnstr(2, 1, header, header_length, curses.A_BOLD)
                except curses.error:
                    pass

                # Draw separator line
                if self.max_y > 3:
                    # Calculate safe separator length
                    separator_length = max(1, min(self.max_x - 2, header_length))
                    separator = "-" * separator_length

                    try:
                        # Use addnstr for safer string display
                        self.screen.addnstr(3, 1, separator, separator_length)
                    except curses.error:
                        pass

            # Draw agents
            if not self.agents:
                if self.max_y > 5 and self.max_x > 5:  # Make sure we have enough space
                    try:
                        # Use addnstr for safer string display
                        self.screen.addnstr(
                            5, 1, "No agents found", min(14, self.max_x - 2)
                        )
                    except curses.error:
                        pass
            else:
                for i, agent in enumerate(self.agents):
                    if 4 + i >= self.max_y - 2:
                        break

                    # Highlight selected row
                    attr = curses.A_REVERSE if i == self.selected_index else 0

                    # Get status
                    status = agent.get("status", AgentStatus.INACTIVE)
                    status_symbol = STATUS_SYMBOLS.get(status, "?")
                    status_color = STATUS_COLORS.get(status, 7)  # Default to white

                    # Format agent ID
                    agent_id = agent.get("agent_id", "")
                    if agent_id and len(agent_id) > 36:
                        agent_id = agent_id[:33] + "..."

                    # Format name
                    name = agent.get("name", "")
                    if name and len(name) > 20:
                        name = name[:17] + "..."

                    # Format model
                    model = agent.get("model_name", "")
                    if model and len(model) > 15:
                        model = model[:12] + "..."

                    # Format port and URI
                    port = (
                        str(agent.get("port", ""))
                        if agent.get("port") is not None
                        else ""
                    )

                    # Handle URI with extra care
                    uri = agent.get("uri", "")
                    if uri is None:
                        uri = ""
                    elif not isinstance(uri, str):
                        # Convert non-string URI to string
                        try:
                            uri = str(uri)
                        except Exception:
                            uri = "<invalid uri>"

                    # Truncate URI if it's too long
                    max_uri_length = max(
                        10, self.max_x - 95
                    )  # Ensure at least 10 chars
                    if len(uri) > max_uri_length:
                        uri = uri[: max_uri_length - 3] + "..."

                    # Draw row
                    row = 4 + i

                    # Status symbol with color - check if we're within screen bounds
                    if (
                        row < self.max_y - 1 and 1 < self.max_x
                    ):  # Ensure we're not at the bottom of the screen
                        try:
                            self.screen.addstr(
                                row,
                                1,
                                status_symbol,
                                curses.color_pair(status_color) | attr,
                            )
                        except curses.error:
                            # Ignore curses errors when writing to the screen
                            pass

                    # Rest of the row - check if we're within screen bounds
                    if (
                        row < self.max_y - 1
                    ):  # Ensure we're not at the bottom of the screen
                        # Check if we have enough horizontal space for each field
                        if 9 < self.max_x:
                            try:
                                # Use addnstr for safer string display
                                self.screen.addnstr(
                                    row, 9, agent_id, self.max_x - 10, attr
                                )
                            except curses.error:
                                pass
                        if 48 < self.max_x:
                            try:
                                # Use addnstr for safer string display
                                self.screen.addnstr(
                                    row, 48, name, self.max_x - 49, attr
                                )
                            except curses.error:
                                pass
                        if 70 < self.max_x:
                            try:
                                # Use addnstr for safer string display
                                self.screen.addnstr(
                                    row, 70, model, self.max_x - 71, attr
                                )
                            except curses.error:
                                pass
                        if 87 < self.max_x:
                            try:
                                # Use addnstr for safer string display
                                self.screen.addnstr(
                                    row, 87, port, self.max_x - 88, attr
                                )
                            except curses.error:
                                pass
                        if 94 < self.max_x:
                            # Extra safety for URI display
                            safe_uri = uri
                            # Ensure we're not trying to write beyond the screen width
                            if len(safe_uri) > (self.max_x - 95):
                                safe_uri = safe_uri[: (self.max_x - 95)]

                            try:
                                # Use addnstr instead of addstr to limit string length
                                self.screen.addnstr(
                                    row, 94, safe_uri, self.max_x - 95, attr
                                )
                            except curses.error:
                                # If still failing, try with a very short string
                                try:
                                    self.screen.addnstr(row, 94, "...", 3, attr)
                                except curses.error:
                                    pass

            # Draw footer - ensure it fits within screen bounds
            if HAS_LOG_VIEWER:
                footer = (
                    "q: Quit | r: Refresh | d: Delete selected agent | c: View console"
                )
            else:
                footer = "q: Quit | r: Refresh | d: Delete selected agent"

            if (
                self.max_y > 1 and self.max_x > 2
            ):  # Make sure we have at least one line and two columns
                # Calculate safe footer length
                footer_length = min(len(footer), self.max_x - 2)

                try:
                    # Use addnstr for safer string display
                    self.screen.addnstr(
                        self.max_y - 1, 1, footer, footer_length, curses.A_BOLD
                    )
                except curses.error:
                    # If still failing, try with a minimal footer
                    try:
                        self.screen.addnstr(
                            self.max_y - 1, 1, "q:Quit", 6, curses.A_BOLD
                        )
                    except curses.error:
                        pass

            self.screen.refresh()
        except Exception as e:
            logger.error(f"Error drawing UI: {e}")


def run_tui():
    """Run the TUI."""
    registry = get_registry()
    tui = AgentManagerTUI(registry)
    tui.start()


if __name__ == "__main__":
    run_tui()
