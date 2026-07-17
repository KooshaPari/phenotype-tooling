import logging
import random

class WrenEngineIntegration:
    """
    Integration with Wren Engine for model selection
    """
    
    def __init__(self, config):
        self.config = config
        self.models = {m['name']: m for m in config.get('models', [])}
        
    def select_model(self, request):
        """
        Select the best model for a given request
        
        Args:
            request: Dict containing request parameters
            
        Returns:
            String containing the selected model name
        """
        prompt = request.get('prompt', '')
        required_capabilities = self._analyze_prompt_requirements(prompt)
        
        # Filter models by required capabilities
        suitable_models = []
        for name, model in self.models.items():
            model_capabilities = set(model.get('capabilities', []))
            if all(cap in model_capabilities for cap in required_capabilities):
                suitable_models.append((name, model))
        
        if not suitable_models:
            logging.warning(f"No suitable models found for capabilities: {required_capabilities}")
            # Fallback to any model
            suitable_models = list(self.models.items())
        
        # Sort by cost (lowest first)
        suitable_models.sort(key=lambda x: x[1].get('cost_per_token', float('inf')))
        
        # Return the cheapest suitable model
        return suitable_models[0][0] if suitable_models else None
    
    def _analyze_prompt_requirements(self, prompt):
        """
        Analyze prompt to determine required capabilities
        
        Args:
            prompt: String containing the prompt
            
        Returns:
            List of required capabilities
        """
        # TODO: Implement more sophisticated analysis
        capabilities = ["basic"]
        
        # Simple keyword-based analysis
        if "code" in prompt.lower() or "function" in prompt.lower():
            capabilities.append("code")
            
        if len(prompt) > 500 or "explain" in prompt.lower() or "analyze" in prompt.lower():
            capabilities.append("reasoning")
            
        if "creative" in prompt.lower() or "story" in prompt.lower() or "imagine" in prompt.lower():
            capabilities.append("creative")
            
        if "complex" in prompt.lower() or "difficult" in prompt.lower():
            capabilities.append("complex-reasoning")
            
        return capabilities
