import os
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI
from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    """
    OpenAI API provider
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key') or os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.available_models = self._get_available_models()
        
    def _get_available_models(self) -> List[str]:
        """Get list of available models from OpenAI"""
        try:
            response = self.client.models.list()
            return [model.id for model in response.data]
        except Exception as e:
            logging.error(f"Error fetching OpenAI models: {str(e)}")
            # Fallback to common models
            return ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        """
        Generate a response using OpenAI API
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional parameters for OpenAI API
            
        Returns:
            Dict containing the response
        """
        model = kwargs.get('model', 'gpt-3.5-turbo')
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **{k: v for k, v in kwargs.items() if k not in ['model']}
            )
            
            return {
                "source": "openai",
                "model": model,
                "text": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            logging.error(f"Error generating response from OpenAI: {str(e)}")
            raise
    
    def get_models(self) -> Dict[str, Any]:
        """
        Get available models from OpenAI
        
        Returns:
            Dict containing model information
        """
        return {
            "provider": "openai",
            "models": self.available_models
        }
