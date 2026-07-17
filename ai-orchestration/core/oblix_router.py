import logging
import os
from typing import Dict, Any, Optional
from .providers import (
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    OpenRouterProvider,
    OllamaProvider,
)


class OblixRouter:
    """
    Oblix router for directing AI requests between cloud and edge models
    """

    def __init__(self, config):
        self.config = config
        self.policies = {
            p["name"]: p for p in config.get("routing_policy", {}).get("policies", [])
        }
        self.default_policy = config.get("routing_policy", {}).get(
            "default", "cost-optimized"
        )

        # Initialize providers
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize AI providers"""
        self.cloud_providers = {}
        self.edge_providers = {}

        # Initialize OpenAI provider if API key is available
        if os.environ.get("OPENAI_API_KEY"):
            self.cloud_providers["openai"] = OpenAIProvider(
                {"api_key": os.environ.get("OPENAI_API_KEY")}
            )
            logging.info("Initialized OpenAI provider")

        # Initialize Anthropic provider if API key is available
        if os.environ.get("ANTHROPIC_API_KEY"):
            self.cloud_providers["anthropic"] = AnthropicProvider(
                {"api_key": os.environ.get("ANTHROPIC_API_KEY")}
            )
            logging.info("Initialized Anthropic provider")

        # Initialize Google provider if API key is available
        if os.environ.get("GOOGLE_API_KEY"):
            self.cloud_providers["google"] = GoogleProvider(
                {"api_key": os.environ.get("GOOGLE_API_KEY"), "use_vertex": False}
            )
            logging.info("Initialized Google AI provider")

        # Initialize Vertex provider if project ID is available
        if os.environ.get("GOOGLE_CLOUD_PROJECT"):
            self.cloud_providers["vertex"] = GoogleProvider(
                {
                    "project_id": os.environ.get("GOOGLE_CLOUD_PROJECT"),
                    "use_vertex": True,
                }
            )
            logging.info("Initialized Vertex AI provider")

        # Initialize OpenRouter provider if API key is available
        if os.environ.get("OPENROUTER_API_KEY"):
            self.cloud_providers["openrouter"] = OpenRouterProvider(
                {"api_key": os.environ.get("OPENROUTER_API_KEY")}
            )
            logging.info("Initialized OpenRouter provider")

        # Initialize Ollama provider
        self.edge_providers["ollama"] = OllamaProvider(
            {"api_base": os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")}
        )
        logging.info("Initialized Ollama provider")

    def route_request(self, request):
        """
        Route a request to either cloud or edge based on policy

        Args:
            request: Dict containing request parameters

        Returns:
            Dict containing the response
        """
        policy_name = request.get("routing_policy", self.default_policy)
        policy = self.policies.get(policy_name, self.policies.get(self.default_policy))

        if not policy:
            raise ValueError(f"No routing policy found: {policy_name}")

        strategy = policy.get("strategy", "edge-first")
        fallback = policy.get("fallback", "fail")

        if strategy == "edge-first":
            try:
                return self._route_to_edge(request)
            except Exception as e:
                logging.warning(f"Edge routing failed: {str(e)}")
                if fallback == "cloud":
                    return self._route_to_cloud(request)
                else:
                    raise

        elif strategy == "cloud-first":
            try:
                return self._route_to_cloud(request)
            except Exception as e:
                logging.warning(f"Cloud routing failed: {str(e)}")
                if fallback == "edge":
                    return self._route_to_edge(request)
                else:
                    raise

        elif strategy == "edge-only":
            return self._route_to_edge(request)

        elif strategy == "cloud-only":
            return self._route_to_cloud(request)

        else:
            raise ValueError(f"Unknown routing strategy: {strategy}")

    def _route_to_edge(self, request):
        """Route request to edge provider"""
        if not self.edge_providers:
            raise ValueError("No edge providers available")

        model = request.get("model")
        provider_name = request.get("provider", "ollama")

        if provider_name not in self.edge_providers:
            provider_name = next(iter(self.edge_providers))

        provider = self.edge_providers[provider_name]

        logging.info(
            f"Routing request to edge provider {provider_name} with model {model}"
        )

        return provider.generate(
            prompt=request.get("prompt", ""),
            max_tokens=request.get("max_tokens", 1000),
            temperature=request.get("temperature", 0.7),
            model=model,
        )

    def _route_to_cloud(self, request):
        """Route request to cloud provider"""
        if not self.cloud_providers:
            raise ValueError("No cloud providers available")

        model = request.get("model")
        provider_name = request.get("provider")

        # If provider is specified and available, use it
        if provider_name and provider_name in self.cloud_providers:
            provider = self.cloud_providers[provider_name]
        # If model is specified, try to determine provider from model name
        elif model:
            provider_name = self._get_provider_for_model(model)
            if provider_name in self.cloud_providers:
                provider = self.cloud_providers[provider_name]
            else:
                # Use first available provider
                provider_name = next(iter(self.cloud_providers))
                provider = self.cloud_providers[provider_name]
        else:
            # Use first available provider
            provider_name = next(iter(self.cloud_providers))
            provider = self.cloud_providers[provider_name]

        logging.info(
            f"Routing request to cloud provider {provider_name} with model {model}"
        )

        return provider.generate(
            prompt=request.get("prompt", ""),
            max_tokens=request.get("max_tokens", 1000),
            temperature=request.get("temperature", 0.7),
            model=model,
        )

    def _get_provider_for_model(self, model: str) -> str:
        """Determine provider based on model name"""
        if not model:
            return next(iter(self.cloud_providers))

        model = model.lower()

        # Check for OpenRouter prefix first
        if model.startswith("openrouter/"):
            return "openrouter"

        if model.startswith("gpt-") or model.startswith("text-davinci-"):
            return "openai"
        elif model.startswith("claude-"):
            return "anthropic"
        elif (
            model.startswith("gemini-")
            or model.startswith("text-bison")
            or model.startswith("chat-bison")
        ):
            return "google" if "google" in self.cloud_providers else "vertex"
        elif "/" in model:  # OpenRouter models are typically in format provider/model
            # If the model contains a slash but doesn't have the openrouter/ prefix,
            # we need to check if it's available from a native provider first
            provider_prefix, model_name = model.split("/", 1)

            # Check if this is a model ID that exists in a native provider
            for provider_name, provider in self.cloud_providers.items():
                if provider_name != "openrouter":
                    provider_models = provider.get_models()
                    if (
                        "models" in provider_models
                        and model_name in provider_models["models"]
                    ):
                        return provider_name

            # If not found in native providers, use OpenRouter
            return "openrouter"

        # Default to first available provider
        return next(iter(self.cloud_providers))
