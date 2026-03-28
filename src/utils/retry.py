"""
Sentinel Retry — High-Resilience Retry logic using tenacity.
"""

import sys
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from config import settings
from src.utils.logger import logger

def sentinel_retry(
    max_attempts: int = None,
    exceptions: tuple = (Exception,),
    base_delay: float = None,
    max_delay: float = 10.0
):
    """
    Standardized Retry Decorator.
    Works for both sync and async functions.
    
    Args:
        max_attempts: Max number of tries. Defaults to settings.API_MAX_RETRIES.
        exceptions: Exceptions to trigger a retry.
        base_delay: Initial delay. Defaults to settings.API_RETRY_DELAY.
        max_delay: Max delay between retries.
    """
    _max_attempts = max_attempts if max_attempts is not None else settings.API_MAX_RETRIES
    _base_delay = base_delay if base_delay is not None else settings.API_RETRY_DELAY

    return retry(
        stop=stop_after_attempt(_max_attempts),
        wait=wait_exponential(multiplier=_base_delay, max=max_delay),
        retry=retry_if_exception_type(exceptions),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True  # Reraise the last exception after all attempts fail
    )

# Backward Compatibility (Alias for the previous decorator name)
retry_on_failure = sentinel_retry
