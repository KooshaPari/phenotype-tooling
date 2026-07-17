"""
Reasoning tests for the SWE agent.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional

from tests.integration.test_base import SWEAgentTestBase


class ReasoningTests(SWEAgentTestBase):
    """
    Reasoning tests for the SWE agent.
    """

    def setUp(self):
        """
        Set up the test.
        """
        super().setUp()

        # Set up the test prompts
        self.basic_prompt = "Hello! What is 1+1?"
        self.tool_check_prompt = "What MCP tools do you have access to?"
        self.sequential_thinking_prompt = (
            "Use Sequential Thinking to solve this problem: "
            "How would you design a system to automatically categorize and tag incoming customer support tickets?"
        )
        self.reasoning_prompt = "Explain the concept of recursion in programming and provide a simple example."

    async def test_reasoning_openai_o4_mini_streaming(self):
        """
        Test reasoning with OpenAI o4-mini model with streaming.
        """
        response = await self.get_completion(
            model="o3-mini",  # Using gpt-4o as a substitute for o4-mini
            provider="openai",
            prompt=self.reasoning_prompt,
            stream=True,
        )

        evaluation = self.evaluate_response(response)

        # Save the results
        self._save_results(
            "reasoning_openai_o4_mini_streaming",
            response,
            evaluation,
        )

    async def test_reasoning_openai_o4_mini_non_streaming(self):
        """
        Test reasoning with OpenAI o4-mini model without streaming.
        """
        response = await self.get_completion(
            model="gpt-4o",  # Using gpt-4o as a substitute for o4-mini
            provider="openai",
            prompt=self.reasoning_prompt,
            stream=False,
        )

        evaluation = self.evaluate_response(response)

        # Save the results
        self._save_results(
            "reasoning_openai_o4_mini_non_streaming",
            response,
            evaluation,
        )

    async def test_reasoning_openrouter_o4_mini_streaming(self):
        """
        Test reasoning with OpenRouter o4-mini model with streaming.
        """
        response = await self.get_completion(
            model="gpt-4o",  # Using gpt-4o as a substitute for o4-mini
            provider="openrouter",
            prompt=self.reasoning_prompt,
            stream=True,
        )

        evaluation = self.evaluate_response(response)

        # Save the results
        self._save_results(
            "reasoning_openrouter_o4_mini_streaming",
            response,
            evaluation,
        )

    async def test_reasoning_openrouter_o4_mini_non_streaming(self):
        """
        Test reasoning with OpenRouter o4-mini model without streaming.
        """
        response = await self.get_completion(
            model="gpt-4o",  # Using gpt-4o as a substitute for o4-mini
            provider="openrouter",
            prompt=self.reasoning_prompt,
            stream=False,
        )

        evaluation = self.evaluate_response(response)

        # Save the results
        self._save_results(
            "reasoning_openrouter_o4_mini_non_streaming",
            response,
            evaluation,
        )

    def _save_results(
        self, test_name: str, response: Dict[str, Any], evaluation: Dict[str, Any]
    ):
        """
        Save the test results to a file.
        """
        # Create the results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(results_dir, exist_ok=True)

        # Save the results
        results = {
            "test_name": test_name,
            "prompt": self.reasoning_prompt,
            "response": {
                "id": response.get("id"),
                "model": response.get("model"),
                "content": response.get("content"),
                "streaming": response.get("streaming"),
            },
            "evaluation": {
                "content_length": evaluation.get("content_length"),
                "has_expected_content": evaluation.get("has_expected_content"),
                "critique": evaluation.get("critique"),
            },
        }

        # Write the results to a file
        with open(os.path.join(results_dir, f"{test_name}.json"), "w") as f:
            json.dump(results, f, indent=2)


async def run_tests():
    """
    Run the tests.
    """
    test = ReasoningTests()
    test.setUp()
    await test.test_reasoning_openai_o4_mini_streaming()
    await test.test_reasoning_openai_o4_mini_non_streaming()
    await test.test_reasoning_openrouter_o4_mini_streaming()
    await test.test_reasoning_openrouter_o4_mini_non_streaming()


if __name__ == "__main__":
    asyncio.run(run_tests())
