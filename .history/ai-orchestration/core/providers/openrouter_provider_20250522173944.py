import os
import logging
import requests
from typing import Dict, Any, Optional, List
from .base import BaseProvider


class OpenRouterProvider(BaseProvider):
    """
    OpenRouter API provider
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key') or os.environ.get('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.api_base = "https://openrouter.ai/api/v1"
        self.available_models = self._get_available_models()
        
    def _get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.api_base}/models", headers=headers)
            response.raise_for_status()
            
            models_data = response.json().get("data", [])
            return models_data
        except Exception as e:
            logging.error(f"Error fetching OpenRouter models: {str(e)}")
            # Fallback to common models
            return [
                {"id": "openai/gpt-4-turbo", "name": "GPT-4 Turbo"},
                {"id": "anthropic/claude-3-opus", "name": "Claude 3 Opus"},
                {"id": "anthropic/claude-3-sonnet", "name": "Claude 3 Sonnet"},
                {"id": "google/gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
                {"id": "meta-llama/llama-3-70b-instruct", "name": "Llama 3 70B"}
            ]
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        """
        Generate a response using OpenRouter API
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional parameters for OpenRouter API
            
        Returns:
            Dict containing the response
        """
        model = kwargs.get('model', 'openai/gpt-3.5-turbo')
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": kwargs.get('referer', 'https://localhost'),  # Required for OpenRouter
                "X-Title": kwargs.get('title', 'AI Orchestration')  # Optional but recommended
            }
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                **{k: v for k, v in kwargs.items() if k not in ['model', 'referer', 'title']}
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            response_data = response.json()
            
            return {
                "source": "openrouter",
                "model": model,
                "text": response_data['choices'][0]['message']['content'],
                "usage": response_data.get('usage', {})
            }
        except Exception as e:
            logging.error(f"Error generating response from OpenRouter: {str(e)}")
            raise
    
    def get_models(self) -> Dict[str, Any]:
        """
        Get available models from OpenRouter
        
        Returns:
            Dict containing model information
        """
        model_ids = [model.get('id') for model in self.available_models]
        
        return {
            "provider": "openrouter",
            "models": model_ids
        }
