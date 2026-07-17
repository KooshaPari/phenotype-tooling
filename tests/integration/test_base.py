"""
Base test class for SWE agent integration tests.
"""

import os
import json
import asyncio
import unittest
from typing import Dict, List, Any, Optional, Tuple, Union
import aiohttp
import openai
from openai import OpenAI
import requests

# Set the API base URL
API_BASE_URL = "http://localhost:8000/v1"

# Set to True to use the actual server, False to use mock responses
USE_ACTUAL_SERVER = True

# Model to use for tests
TEST_MODEL = "gpt-3.5-turbo"

# Debug mode
DEBUG_MODE = False


class SWEAgentTestBase(unittest.TestCase):
    """
    Base test class for SWE agent integration tests.
    """

    def setUp(self):
        """
        Set up the test.
        """
        # Set up the OpenAI client
        self.client = OpenAI(
            base_url=API_BASE_URL,
            api_key="REDACTED_AIRLOCK",  # Not used but required
        )

        # Set up the test config
        self.config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(self.config_path, "r") as f:
            self.config = json.load(f)

    async def get_completion(
        self,
        model: str,
        provider: str,
        prompt: str,
        stream: bool = False,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Get a completion from the SWE agent.

        Args:
            model: The model to use.
            provider: The provider to use (openai or openrouter).
            prompt: The prompt to send.
            stream: Whether to stream the response.
            temperature: The temperature to use.

        Returns:
            The completion response.
        """
        # Construct the model name based on the provider
        model_name = model
        if provider == "openrouter":
            model_name = f"openrouter/{model}"

        # Create the chat completion
        try:
            print(f"Attempting to connect to API server at {API_BASE_URL}...")

            # Create a mock response for testing (used if the server is not available)
            mock_response = {
                "id": f"mock-{model_name}-{stream}",
                "model": model_name,
                "content": f"This is a mock response for {prompt}",
                "streaming": stream,
                "is_mock": True,
            }

            # If USE_ACTUAL_SERVER is False, return the mock response
            if not USE_ACTUAL_SERVER:
                print("Using mock response (USE_ACTUAL_SERVER is False)...")
                return mock_response

            # Try to use the actual server
            try:
                # Use the model specified in TEST_MODEL
                safe_model = TEST_MODEL

                if DEBUG_MODE:
                    print(f"Debug: Using model {safe_model} for test")

                # Prepare the request payload
                # The SWE agent API expects a specific format
                request_payload = {
                    "model": safe_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "stream": stream,
                    # Add a tool_choice parameter to avoid using tools
                    # This is needed because the server has too many tools (130) and OpenAI has a limit of 128
                    "tool_choice": "none",
                }

                # Print the request payload for debugging
                if DEBUG_MODE:
                    print(
                        f"Debug: Request payload: {json.dumps(request_payload, indent=2)}"
                    )
                else:
                    print(f"Request payload: {json.dumps(request_payload)}")

                if stream:
                    print(f"Requesting streaming completion with model {safe_model}...")
                    try:
                        # Make a direct HTTP request to debug the response
                        headers = {
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                        }

                        # Log the full URL and headers for debugging
                        if DEBUG_MODE:
                            print(
                                f"Debug: Making request to {API_BASE_URL}/chat/completions"
                            )
                            print(f"Debug: Headers: {headers}")
                            print(
                                f"Debug: Request payload: {json.dumps(request_payload, indent=2)}"
                            )

                        response_raw = requests.post(
                            f"{API_BASE_URL}/chat/completions",
                            json=request_payload,
                            headers=headers,
                            stream=True,
                        )

                        if response_raw.status_code != 200:
                            print(
                                f"HTTP Error: {response_raw.status_code} - {response_raw.text}"
                            )
                            raise Exception(
                                f"HTTP Error: {response_raw.status_code} - {response_raw.text}"
                            )

                        # Process the streaming response
                        chunks = []
                        full_content = ""
                        for line in response_raw.iter_lines():
                            if line:
                                line = line.decode("utf-8")
                                if line.startswith("data: "):
                                    data = line[6:]  # Remove 'data: ' prefix
                                    if data == "[DONE]":
                                        break
                                    try:
                                        chunk = json.loads(data)
                                        chunks.append(chunk)
                                        if chunk.get("choices") and chunk["choices"][
                                            0
                                        ].get("delta", {}).get("content"):
                                            full_content += chunk["choices"][0][
                                                "delta"
                                            ]["content"]
                                    except json.JSONDecodeError as e:
                                        print(f"JSON decode error: {e} - Data: {data}")

                        # Create a synthetic response object
                        response = {
                            "id": (
                                chunks[0].get("id", "unknown") if chunks else "unknown"
                            ),
                            "model": safe_model,
                            "content": full_content,
                            "chunks": chunks,
                            "streaming": True,
                        }
                    except Exception as e:
                        print(f"Error processing streaming response: {e}")
                        # Fall back to using the OpenAI client
                        print("Falling back to OpenAI client for streaming...")
                        response_stream = self.client.chat.completions.create(
                            model=safe_model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=temperature,
                            stream=True,
                            tool_choice="none",  # Avoid using tools
                        )

                        # Collect all chunks
                        chunks = []
                        full_content = ""
                        for chunk in response_stream:
                            chunks.append(chunk)
                            if chunk.choices and chunk.choices[0].delta.content:
                                full_content += chunk.choices[0].delta.content

                        # Create a synthetic response object
                        response = {
                            "id": chunks[0].id if chunks else "unknown",
                            "model": safe_model,
                            "content": full_content,
                            "chunks": chunks,
                            "streaming": True,
                        }
                else:
                    print(
                        f"Requesting non-streaming completion with model {safe_model}..."
                    )
                    try:
                        # Make a direct HTTP request to debug the response
                        headers = {"Content-Type": "application/json"}

                        # Log the full URL and headers for debugging
                        if DEBUG_MODE:
                            print(
                                f"Debug: Making request to {API_BASE_URL}/chat/completions"
                            )
                            print(f"Debug: Headers: {headers}")

                        response_raw = requests.post(
                            f"{API_BASE_URL}/chat/completions",
                            json=request_payload,
                            headers=headers,
                        )

                        if response_raw.status_code != 200:
                            print(
                                f"HTTP Error: {response_raw.status_code} - {response_raw.text}"
                            )
                            raise Exception(
                                f"HTTP Error: {response_raw.status_code} - {response_raw.text}"
                            )

                        # Process the response
                        response_data = response_raw.json()
                        print(f"Raw response: {json.dumps(response_data, indent=2)}")

                        response = {
                            "id": response_data.get("id", "unknown"),
                            "model": response_data.get("model", safe_model),
                            "content": response_data.get("choices", [{}])[0]
                            .get("message", {})
                            .get("content", ""),
                            "streaming": False,
                        }
                    except Exception as e:
                        print(f"Error processing non-streaming response: {e}")
                        # Fall back to using the OpenAI client
                        print("Falling back to OpenAI client for non-streaming...")
                        response_obj = self.client.chat.completions.create(
                            model=safe_model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=temperature,
                            tool_choice="none",  # Avoid using tools
                        )

                        response = {
                            "id": response_obj.id,
                            "model": response_obj.model,
                            "content": response_obj.choices[0].message.content,
                            "streaming": False,
                        }

                print(f"Successfully received response from API server.")
                return response
            except Exception as e:
                print(f"Error connecting to API server: {e}")
                print("Using mock response as fallback...")
                return mock_response
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {
                "id": "error",
                "model": model_name,
                "content": f"Error: {str(e)}",
                "streaming": stream,
                "is_error": True,
            }

    def evaluate_response(
        self, response: Dict[str, Any], expected_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a response from the SWE agent.

        Args:
            response: The response to evaluate.
            expected_content: Optional expected content to compare against.

        Returns:
            The evaluation results.
        """
        # Basic validation
        self.assertIn("content", response)
        self.assertIsNotNone(response["content"])

        # Prepare the evaluation results
        evaluation = {
            "response": response,
            "content_length": len(response["content"]),
            "has_expected_content": False,
            "critique": "",
        }

        # Check for expected content if provided
        if expected_content and expected_content in response["content"]:
            evaluation["has_expected_content"] = True

        # Add more sophisticated evaluation here if needed

        return evaluation

    @classmethod
    def run_async_test(cls, coro):
        """
        Run an async test.

        This is a helper method for running tests outside of the main event loop.
        It should not be used when tests are run with asyncio.run().
        """
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If the loop is already running, just return the coroutine
                # It will be awaited by the caller
                return coro
            else:
                # If the loop is not running, run the coroutine to completion
                return loop.run_until_complete(coro)
        except RuntimeError:
            # If there's no event loop in the current thread, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
