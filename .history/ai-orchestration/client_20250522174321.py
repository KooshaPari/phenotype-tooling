import requests
import json
from typing import Dict, List, Any, Optional


class AIOrchestrationClient:
    """
    Client for the AI Orchestration API
    """

    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url

    def generate(
        self,
        prompt: str,
        routing_policy: str = "default",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        plugins: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a response using the AI orchestration system

        Args:
            prompt: The input prompt
            routing_policy: Routing policy to use (default, cost-optimized, performance, privacy)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            plugins: List of plugin IDs to use

        Returns:
            Dict containing the response
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "prompt": prompt,
            "routing_policy": routing_policy,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "plugins": plugins or [],
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List available plugins

        Returns:
            List of available plugins
        """
        url = f"{self.base_url}/api/plugins"
        response = requests.get(url)
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

        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
