import os
import logging
from typing import Dict, Any, Optional, List
import anthropic
from .base import BaseProvider


class AnthropicProvider(BaseProvider):
    """
    Anthropic API provider
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key') or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.available_models = self._get_available_models()
        
    def _get_available_models(self) -> List[str]:
        """Get list of available models from Anthropic"""
        # Anthropic doesn't have a list models endpoint, so we hardcode the available models
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2"
        ]
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        """
        Generate a response using Anthropic API
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional parameters for Anthropic API
            
        Returns:
            Dict containing the response
        """
        model = kwargs.get('model', 'claude-3-sonnet-20240229')
        
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **{k: v for k, v in kwargs.items() if k not in ['model']}
            )
            
            return {
                "source": "anthropic",
                "model": model,
                "text": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
        except Exception as e:
            logging.error(f"Error generating response from Anthropic: {str(e)}")
            raise
    
    def get_models(self) -> Dict[str, Any]:
        """
        Get available models from Anthropic
        
        Returns:
            Dict containing model information
        """
        return {
            "provider": "anthropic",
            "models": self.available_models
        }
