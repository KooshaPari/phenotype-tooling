import os
import logging
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from google.cloud import aiplatform
from .base import BaseProvider


class GoogleProvider(BaseProvider):
    """
    Google AI/Vertex API provider
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key') or os.environ.get('GOOGLE_API_KEY')
        self.project_id = config.get('project_id') or os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.location = config.get('location') or os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
        self.use_vertex = config.get('use_vertex', False)
        
        if self.use_vertex and not self.project_id:
            raise ValueError("Google Cloud project ID is required for Vertex AI")
        
        if not self.use_vertex and not self.api_key:
            raise ValueError("Google API key is required for Google AI")
        
        if self.use_vertex:
            aiplatform.init(project=self.project_id, location=self.location)
        else:
            genai.configure(api_key=self.api_key)
        
        self.available_models = self._get_available_models()
        
    def _get_available_models(self) -> List[str]:
        """Get list of available models from Google"""
        if self.use_vertex:
            # Vertex AI models
            return [
                "gemini-1.0-pro",
                "gemini-1.0-pro-vision",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "text-bison",
                "chat-bison"
            ]
        else:
            # Google AI models
            try:
                models = genai.list_models()
                return [model.name for model in models]
            except Exception as e:
                logging.error(f"Error fetching Google AI models: {str(e)}")
                # Fallback to common models
                return [
                    "gemini-1.0-pro",
                    "gemini-1.5-pro",
                    "gemini-1.5-flash"
                ]
    
    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, **kwargs) -> Dict[str, Any]:
        """
        Generate a response using Google AI/Vertex API
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional parameters for Google API
            
        Returns:
            Dict containing the response
        """
        model_name = kwargs.get('model', 'gemini-1.5-pro')
        
        try:
            if self.use_vertex:
                # Use Vertex AI
                parameters = {
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    **{k: v for k, v in kwargs.items() if k not in ['model']}
                }
                
                model = aiplatform.GenerativeModel(model_name=model_name)
                response = model.generate_content(prompt, generation_config=parameters)
                
                return {
                    "source": "vertex",
                    "model": model_name,
                    "text": response.text
                }
            else:
                # Use Google AI
                model = genai.GenerativeModel(model_name=model_name)
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                        **{k: v for k, v in kwargs.items() if k not in ['model']}
                    }
                )
                
                return {
                    "source": "google",
                    "model": model_name,
                    "text": response.text
                }
        except Exception as e:
            logging.error(f"Error generating response from Google: {str(e)}")
            raise
    
    def get_models(self) -> Dict[str, Any]:
        """
        Get available models from Google
        
        Returns:
            Dict containing model information
        """
        return {
            "provider": "google" if not self.use_vertex else "vertex",
            "models": self.available_models
        }
