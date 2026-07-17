from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseProvider(ABC):
    """
    Base class for AI providers
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        """
        Generate a response from the AI provider
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict containing the response
        """
        pass

    @abstractmethod
    def get_models(self) -> Dict[str, Any]:
        """
        Get available models from the provider
        
        Returns:
            Dict containing model information
        """
        pass
