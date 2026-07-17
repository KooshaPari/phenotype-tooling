"""
Prompt cache monitoring system.

This module provides functionality for monitoring prompt cache usage,
including tracking cache hits, misses, and costs.
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import threading
import logging

# Import Prometheus metrics
try:
    from ..api.main import (
        CACHE_HIT_COUNT,
        CACHE_MISS_COUNT,
        CACHE_HIT_TOKENS,
        CACHE_WRITE_TOKENS,
        CACHE_COST_SAVED,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from ..config.prompt_cache_config import get_prompt_cache_pricing

# Create the cache logs directory if it doesn't exist
CACHE_LOGS_DIR = Path(__file__).parent.parent.parent / "logs" / "cache"
CACHE_LOGS_DIR.mkdir(exist_ok=True, parents=True)

# Create a logger for the cache monitor
logger = logging.getLogger("prompt_cache_monitor")
logger.setLevel(logging.INFO)

# Create a file handler for the cache monitor
cache_handler = logging.FileHandler(CACHE_LOGS_DIR / "prompt_cache.log")
cache_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(cache_handler)


class PromptCacheMonitor:
    """
    Monitor for prompt cache usage.
    """

    def __init__(self):
        """Initialize the prompt cache monitor."""
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.cache_hit_tokens: int = 0
        self.cache_miss_tokens: int = 0
        self.cache_write_tokens: int = 0
        self.cache_read_tokens: int = 0
        self.total_cost_saved: float = 0.0
        self.requests_with_cache: int = 0
        self.total_requests: int = 0
        self.model_stats: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

        # Initialize the cache log file
        self.cache_log_file = CACHE_LOGS_DIR / "cache_stats.json"
        self._load_stats()

    def _load_stats(self):
        """Load stats from the cache log file."""
        if self.cache_log_file.exists():
            try:
                with open(self.cache_log_file, "r") as f:
                    stats = json.load(f)
                    self.cache_hits = stats.get("cache_hits", 0)
                    self.cache_misses = stats.get("cache_misses", 0)
                    self.cache_hit_tokens = stats.get("cache_hit_tokens", 0)
                    self.cache_miss_tokens = stats.get("cache_miss_tokens", 0)
                    self.cache_write_tokens = stats.get("cache_write_tokens", 0)
                    self.cache_read_tokens = stats.get("cache_read_tokens", 0)
                    self.total_cost_saved = stats.get("total_cost_saved", 0.0)
                    self.requests_with_cache = stats.get("requests_with_cache", 0)
                    self.total_requests = stats.get("total_requests", 0)
                    self.model_stats = stats.get("model_stats", {})
            except Exception as e:
                logger.error(f"Error loading cache stats: {e}")

    def _save_stats(self):
        """Save stats to the cache log file."""
        try:
            stats = {
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "cache_hit_tokens": self.cache_hit_tokens,
                "cache_miss_tokens": self.cache_miss_tokens,
                "cache_write_tokens": self.cache_write_tokens,
                "cache_read_tokens": self.cache_read_tokens,
                "total_cost_saved": self.total_cost_saved,
                "requests_with_cache": self.requests_with_cache,
                "total_requests": self.total_requests,
                "model_stats": self.model_stats,
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.cache_log_file, "w") as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache stats: {e}")

    def log_request(
        self,
        request_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cache_write_tokens: Optional[int] = None,
        cache_read_tokens: Optional[int] = None,
        cache_hit: Optional[bool] = None,
    ):
        """
        Log a request to the cache monitor.

        Args:
            request_id: The request ID.
            model: The model used.
            input_tokens: The number of input tokens.
            output_tokens: The number of output tokens.
            cache_write_tokens: The number of tokens written to the cache.
            cache_read_tokens: The number of tokens read from the cache.
            cache_hit: Whether the request was a cache hit.
        """
        with self.lock:
            # Update global stats
            self.total_requests += 1

            # Calculate costs
            model_pricing = get_prompt_cache_pricing(model)
            normal_input_cost = (input_tokens / 1_000_000) * model_pricing.get(
                "input", 0.0
            )
            normal_output_cost = (output_tokens / 1_000_000) * model_pricing.get(
                "output", 0.0
            )

            # Initialize model stats if not exists
            if model not in self.model_stats:
                self.model_stats[model] = {
                    "requests": 0,
                    "cache_hits": 0,
                    "cache_misses": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cache_write_tokens": 0,
                    "cache_read_tokens": 0,
                    "cost_saved": 0.0,
                }

            # Update model stats
            self.model_stats[model]["requests"] += 1
            self.model_stats[model]["input_tokens"] += input_tokens
            self.model_stats[model]["output_tokens"] += output_tokens

            # Handle cache stats if available
            if cache_hit is not None:
                self.requests_with_cache += 1

                if cache_hit:
                    self.cache_hits += 1
                    self.model_stats[model]["cache_hits"] += 1

                    # Update Prometheus metrics if available
                    if PROMETHEUS_AVAILABLE:
                        CACHE_HIT_COUNT.labels(model=model).inc()

                    # Calculate cost saved
                    if cache_read_tokens is not None:
                        self.cache_read_tokens += cache_read_tokens
                        self.model_stats[model][
                            "cache_read_tokens"
                        ] += cache_read_tokens

                        # Update Prometheus metrics if available
                        if PROMETHEUS_AVAILABLE:
                            CACHE_HIT_TOKENS.labels(model=model).inc(cache_read_tokens)

                        # Cost calculation for cache read
                        cache_read_cost = (
                            cache_read_tokens / 1_000_000
                        ) * model_pricing.get("read", 0.0)
                        cost_saved = normal_input_cost - cache_read_cost

                        self.total_cost_saved += cost_saved
                        self.model_stats[model]["cost_saved"] += cost_saved

                        # Update Prometheus metrics if available
                        if PROMETHEUS_AVAILABLE:
                            CACHE_COST_SAVED.labels(model=model).inc(cost_saved)

                        logger.info(
                            f"Cache hit for {model}: {cache_read_tokens} tokens read, "
                            f"${cost_saved:.6f} saved"
                        )
                else:
                    self.cache_misses += 1
                    self.model_stats[model]["cache_misses"] += 1

                    # Update Prometheus metrics if available
                    if PROMETHEUS_AVAILABLE:
                        CACHE_MISS_COUNT.labels(model=model).inc()

                    # Track cache write tokens if available
                    if cache_write_tokens is not None:
                        self.cache_write_tokens += cache_write_tokens
                        self.model_stats[model][
                            "cache_write_tokens"
                        ] += cache_write_tokens

                        # Update Prometheus metrics if available
                        if PROMETHEUS_AVAILABLE:
                            CACHE_WRITE_TOKENS.labels(model=model).inc(
                                cache_write_tokens
                            )

                        logger.info(
                            f"Cache miss for {model}: {cache_write_tokens} tokens written to cache"
                        )

            # Save stats
            self._save_stats()

            # Log the request
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "request_id": request_id,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cache_write_tokens": cache_write_tokens,
                "cache_read_tokens": cache_read_tokens,
                "cache_hit": cache_hit,
                "normal_input_cost": normal_input_cost,
                "normal_output_cost": normal_output_cost,
            }

            # Add cache-specific fields if available
            if cache_hit is not None and cache_hit and cache_read_tokens is not None:
                cache_read_cost = (cache_read_tokens / 1_000_000) * model_pricing.get(
                    "read", 0.0
                )
                cost_saved = normal_input_cost - cache_read_cost
                log_entry["cache_read_cost"] = cache_read_cost
                log_entry["cost_saved"] = cost_saved
            elif (
                cache_hit is not None
                and not cache_hit
                and cache_write_tokens is not None
            ):
                cache_write_cost = (cache_write_tokens / 1_000_000) * model_pricing.get(
                    "write", 0.0
                )
                log_entry["cache_write_cost"] = cache_write_cost

            # Write to log file
            with open(CACHE_LOGS_DIR / "prompt_cache_requests.log", "a") as f:
                f.write(json.dumps(log_entry) + "\n")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get the current cache stats.

        Returns:
            A dictionary containing the current cache stats.
        """
        with self.lock:
            return {
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "cache_hit_rate": self.cache_hits / max(self.requests_with_cache, 1),
                "cache_hit_tokens": self.cache_hit_tokens,
                "cache_miss_tokens": self.cache_miss_tokens,
                "cache_write_tokens": self.cache_write_tokens,
                "cache_read_tokens": self.cache_read_tokens,
                "total_cost_saved": self.total_cost_saved,
                "requests_with_cache": self.requests_with_cache,
                "total_requests": self.total_requests,
                "model_stats": self.model_stats,
            }

    def reset_stats(self):
        """Reset all cache stats."""
        with self.lock:
            self.cache_hits = 0
            self.cache_misses = 0
            self.cache_hit_tokens = 0
            self.cache_miss_tokens = 0
            self.cache_write_tokens = 0
            self.cache_read_tokens = 0
            self.total_cost_saved = 0.0
            self.requests_with_cache = 0
            self.total_requests = 0
            self.model_stats = {}
            self._save_stats()


# Create a singleton instance
prompt_cache_monitor = PromptCacheMonitor()
