"""
Retry Utility — Exponential backoff for unreliable external calls.

Usage:
    from src.utils.retry import retry_on_failure

    @retry_on_failure
    def my_api_call():
        ...
"""

import time
from functools import wraps
from typing import Callable, Any

from config import settings
from src.utils.logger import logger


def retry_on_failure(
    func: Callable | None = None,
    *,
    max_retries: int | None = None,
    base_delay: float | None = None,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator that retries a function on failure with exponential backoff.

    Can be used with or without arguments:
        @retry_on_failure
        def f(): ...

        @retry_on_failure(max_retries=5)
        def f(): ...

    Args:
        max_retries: Override config default. Falls back to settings.API_MAX_RETRIES.
        base_delay: Override config default. Falls back to settings.API_RETRY_DELAY.
        exceptions: Tuple of exception types to catch. Default: all Exceptions.
    """
    _max_retries = max_retries if max_retries is not None else settings.API_MAX_RETRIES
    _base_delay = base_delay if base_delay is not None else settings.API_RETRY_DELAY

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None

            for attempt in range(1, _max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < _max_retries:
                        delay = _base_delay * (2 ** (attempt - 1))
                        logger.warning(
                            f"[Retry {attempt}/{_max_retries}] "
                            f"{fn.__name__} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"[Retry {attempt}/{_max_retries}] "
                            f"{fn.__name__} failed permanently: {e}"
                        )

            return None  # all retries exhausted

        return wrapper

    # Support both @retry_on_failure and @retry_on_failure(...)
    if func is not None:
        return decorator(func)
    return decorator
