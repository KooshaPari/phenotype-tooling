import os
import logging
import requests
from typing import Dict, Any, Optional, List
from .base import BaseProvider


class OllamaProvider(BaseProvider):
    """
    Ollama API provider for edge models
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base = config.get('api_base', 'http://localhost:11434')
        self.available_models = self._get_available_models()
        
    def _get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from Ollama"""
        try:
            response = requests.get(f"{self.api_base}/api/tags")
            response.raise_for_status()
            
            models_data = response.json().get("models", [])
            return models_data
        except Exception as e:
            logging.error(f"Error fetching Ollama models: {str(e)}")
            # Fallback to common models
            return [
                {"name": "llama3", "modified_at": "2023-05-01T00:00:00Z"},
                {"name": "mistral", "modified_at": "2023-05-01T00:00:00Z"},
                {"name": "gemma", "modified_at": "2023-05-01T00:00:00Z"}
            ]
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        """
        Generate a response using Ollama API
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional parameters for Ollama API
            
        Returns:
            Dict containing the response
        """
        model = kwargs.get('model', 'llama3')
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    **{k: v for k, v in kwargs.items() if k not in ['model']}
                }
            }
            
            response = requests.post(
                f"{self.api_base}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            response_data = response.json()
            
            return {
                "source": "ollama",
                "model": model,
                "text": response_data.get('response', ''),
                "usage": {
                    "eval_count": response_data.get('eval_count', 0),
                    "eval_duration": response_data.get('eval_duration', 0)
                }
            }
        except Exception as e:
            logging.error(f"Error generating response from Ollama: {str(e)}")
            raise
    
    def get_models(self) -> Dict[str, Any]:
        """
        Get available models from Ollama
        
        Returns:
            Dict containing model information
        """
        model_names = [model.get('name') for model in self.available_models]
        
        return {
            "provider": "ollama",
            "models": model_names
        }
