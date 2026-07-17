import requests
import json
import time
from typing import Dict, List, Any, Optional, Union


class AIOrchestrationClient:
    """
    Client for the AI Orchestration API
    """

    def __init__(
        self, base_url: str = "http://localhost:9000", api_key: Optional[str] = None
    ):
        self.base_url = base_url
        self.api_key = api_key

    def generate(
        self,
        prompt: str,
        routing_policy: str = "default",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        plugins: List[str] = None,
        model: Optional[str] = None,
        use_openai_format: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a response using the AI orchestration system

        Args:
            prompt: The input prompt
            routing_policy: Routing policy to use (default, cost-optimized, performance, privacy)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            plugins: List of plugin IDs to use
            model: Specific model to use
            use_openai_format: Whether to use OpenAI-compatible API format

        Returns:
            Dict containing the response
        """
        if use_openai_format:
            return self.chat_completions(
                messages=[{"role": "user", "content": prompt}],
                model=model or "gpt-3.5-turbo",
                max_tokens=max_tokens,
                temperature=temperature,
            )

        url = f"{self.base_url}/api/generate"
        payload = {
            "prompt": prompt,
            "routing_policy": routing_policy,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "plugins": plugins or [],
            "model": model,
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List available plugins

        Returns:
            List of available plugins
        """
        url = f"{self.base_url}/api/plugins"

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("plugins", [])

    def register_plugin(
        self,
        name: str,
        endpoint: str,
        capabilities: List[str],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a new plugin

        Args:
            name: Plugin name
            endpoint: Plugin endpoint URL
            capabilities: List of plugin capabilities
            description: Optional plugin description

        Returns:
            Dict containing registration status
        """
        url = f"{self.base_url}/api/plugins/register"
        payload = {
            "name": name,
            "endpoint": endpoint,
            "capabilities": capabilities,
            "description": description or f"{name} plugin",
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
