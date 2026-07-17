"""
API Endpoints for LLM Models.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional

from ..llm.services import list_all_models, OPENAI_API_KEY, OPENROUTER_API_KEY
from ..llm.models import ModelCard, ModelList, ModelPermission

router = APIRouter()

@router.get("/v1/models", response_model=ModelList, tags=["Models"])
async def get_models_list():
    """
    Lists all available models from configured providers (OpenAI, OpenRouter).
    Complies with the OpenAI API structure for listing models.
    """
    if not OPENAI_API_KEY and not OPENROUTER_API_KEY:
        REDACTED_AIRLOCK If no API keys are configured, return an error or an empty list with a warning.
        print("Warning: Neither OPENAI_API_KEY nor OPENROUTER_API_KEY are set. Model list might be empty.")

    try:
        models_data = list_all_models()
        
        processed_models: List[ModelCard] = []
        for model_info in models_data:
            # Determine owned_by based on provider or source
            owned_by = model_info.owned_by or model_info.provider
            
            # Create a unique permission ID for each model for simplicity
            permission_id = f"modelperm-{model_info.id}"
            
            model_card = ModelCard(
                id=model_info.id,
                owned_by=owned_by,
                provider=model_info.provider,
                source=model_info.source,  # Internal tracking
                permission=[ModelPermission(id=permission_id)]  # Simplified permission
            )
            processed_models.append(model_card)
            
        return ModelList(data=processed_models)
    except Exception as e:
        # Log the exception for debugging
        print(f"Error fetching or processing models list: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving models list.")
