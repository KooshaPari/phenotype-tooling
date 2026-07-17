"""
API endpoints for prompt cache management.

This module provides REST API endpoints for managing prompt caching,
including getting cache stats and controlling cache behavior.
"""

from typing import Dict, List, Optional, Any, Union
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..utils.prompt_cache_monitor import prompt_cache_monitor
from ..config.prompt_cache_config import (
    DEFAULT_PROMPT_CACHE_CONFIG,
    is_prompt_caching_supported,
    get_prompt_cache_pricing,
    PROMPT_CACHE_SUPPORTED_MODELS,
)

router = APIRouter(prefix="/v1/cache", tags=["cache"])


class CacheStats(BaseModel):
    """Model for cache stats."""
    cache_hits: int
    cache_misses: int
    cache_hit_rate: float
    cache_hit_tokens: int
    cache_miss_tokens: int
    cache_write_tokens: int
    cache_read_tokens: int
    total_cost_saved: float
    requests_with_cache: int
    total_requests: int
    model_stats: Dict[str, Dict[str, Any]]


class CacheConfig(BaseModel):
    """Model for cache configuration."""
    enabled: bool = True
    max_cache_size: int = 1000
    cache_ttl: int = 86400  # 24 hours in seconds


@router.get("/stats", response_model=CacheStats)
async def get_cache_stats():
    """
    Get prompt cache statistics.
    
    Returns:
        Cache statistics.
    """
    try:
        stats = prompt_cache_monitor.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")


@router.post("/reset", response_model=Dict[str, bool])
async def reset_cache_stats():
    """
    Reset prompt cache statistics.
    
    Returns:
        Success status.
    """
    try:
        prompt_cache_monitor.reset_stats()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting cache stats: {str(e)}")


@router.get("/config", response_model=CacheConfig)
async def get_cache_config():
    """
    Get prompt cache configuration.
    
    Returns:
        Cache configuration.
    """
    try:
        return CacheConfig(
            enabled=DEFAULT_PROMPT_CACHE_CONFIG["enabled"],
            max_cache_size=DEFAULT_PROMPT_CACHE_CONFIG["max_cache_size"],
            cache_ttl=DEFAULT_PROMPT_CACHE_CONFIG["cache_ttl"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache config: {str(e)}")


@router.put("/config", response_model=CacheConfig)
async def update_cache_config(config: CacheConfig):
    """
    Update prompt cache configuration.
    
    Args:
        config: Cache configuration.
        
    Returns:
        Updated cache configuration.
    """
    try:
        # Update the global configuration
        DEFAULT_PROMPT_CACHE_CONFIG["enabled"] = config.enabled
        DEFAULT_PROMPT_CACHE_CONFIG["max_cache_size"] = config.max_cache_size
        DEFAULT_PROMPT_CACHE_CONFIG["cache_ttl"] = config.cache_ttl
        
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating cache config: {str(e)}")


@router.get("/supported-models", response_model=List[str])
async def get_supported_models():
    """
    Get models that support prompt caching.
    
    Returns:
        List of model IDs that support prompt caching.
    """
    try:
        return list(PROMPT_CACHE_SUPPORTED_MODELS)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting supported models: {str(e)}")


@router.get("/model-pricing", response_model=Dict[str, Dict[str, float]])
async def get_model_pricing(model_id: Optional[str] = None):
    """
    Get prompt cache pricing for models.
    
    Args:
        model_id: Optional model ID to get pricing for.
        
    Returns:
        Pricing information for models.
    """
    try:
        if model_id:
            if not is_prompt_caching_supported(model_id):
                raise HTTPException(
                    status_code=404, detail=f"Model '{model_id}' does not support prompt caching"
                )
            return {model_id: get_prompt_cache_pricing(model_id)}
        else:
            # Return pricing for all supported models
            pricing = {}
            for model in PROMPT_CACHE_SUPPORTED_MODELS:
                pricing[model] = get_prompt_cache_pricing(model)
            return pricing
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model pricing: {str(e)}")


@router.get("/model-stats", response_model=Dict[str, Dict[str, Any]])
async def get_model_stats(model_id: Optional[str] = None):
    """
    Get prompt cache statistics for models.
    
    Args:
        model_id: Optional model ID to get stats for.
        
    Returns:
        Statistics for models.
    """
    try:
        stats = prompt_cache_monitor.get_stats()
        model_stats = stats.get("model_stats", {})
        
        if model_id:
            if model_id not in model_stats:
                return {model_id: {
                    "requests": 0,
                    "cache_hits": 0,
                    "cache_misses": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cache_write_tokens": 0,
                    "cache_read_tokens": 0,
                    "cost_saved": 0.0,
                }}
            return {model_id: model_stats[model_id]}
        else:
            return model_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model stats: {str(e)}")
