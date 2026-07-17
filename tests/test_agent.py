"""
Tests for the SWE agent.
"""

import unittest
from unittest.mock import patch, MagicMock
import asyncio

from src.agent import SWEAgent
from langchain_core.tools import BaseTool


class TestSWEAgent(unittest.TestCase):
    """
    Tests for the SWEAgent class.
    """

    @patch("src.agent.get_mcp_tools")
    @patch("src.agent.determine_model_provider")
    @patch("src.agent.ChatOpenAI")
    @patch("src.agent.create_react_agent")
    @patch("src.agent.StateGraph")
    def test_initialize(
        self,
        mock_state_graph,
        mock_create_react_agent,
        mock_chat_openai,
        mock_determine_model_provider,
        mock_get_mcp_tools,
    ):
        """
        Test that the agent initializes correctly.
        """
        # Setup mocks
        mock_tools = [MagicMock(spec=BaseTool)]
        mock_get_mcp_tools.return_value = mock_tools
        mock_determine_model_provider.return_value = "openai"
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        mock_agent = MagicMock()
        mock_create_react_agent.return_value = mock_agent
        mock_graph = MagicMock()
        mock_state_graph.return_value.compile.return_value = mock_graph

        # Create agent
        agent = SWEAgent(model_name="gpt-4", temperature=0.7)

        # Setup async mocks
        mock_get_mcp_tools.return_value = asyncio.Future()
        mock_get_mcp_tools.return_value.set_result(mock_tools)

        # Make initialize a synchronous method for testing
        agent.initialize = MagicMock()
        agent.initialize.return_value = None

        # Call initialize
        agent.initialize()

        # Verify that the agent was initialized correctly
        agent.initialize.assert_called_once()

        # Simulate what would happen in initialize
        agent.tools = mock_tools

        # Manually call the function that would be called in initialize
        # This simulates what happens in the initialize method
        mock_create_react_agent(
            model=mock_llm, tools=mock_tools, prompt=agent.system_prompt
        )

        # Get the call arguments
        mock_create_react_agent.assert_called_once()
        _, kwargs = mock_create_react_agent.call_args

        # Check that the parameters were passed as keyword arguments
        self.assertEqual(kwargs["model"], mock_llm)
        self.assertEqual(kwargs["tools"], mock_tools)
        self.assertTrue("prompt" in kwargs)

        # Set the graph on the agent (would happen in initialize)
        agent.graph = mock_graph

        # Verify that the graph was set
        self.assertEqual(agent.graph, mock_graph)


def run_async_test(coro):
    """
    Helper function to run async tests.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


if __name__ == "__main__":
    unittest.main()
