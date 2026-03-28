"""
Sentinel HTTP Client — Global AsyncClient singleton for connection pooling and resilience.
Follows the "AirShield Upgrade Prompt" standards for production-grade networking.
"""

import httpx
from typing import Optional
from src.utils.logger import logger

class SentinelClient:
    """Singleton AsyncClient to prevent socket exhaustion and improve performance."""
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        """Get the global AsyncClient. Initializes it if it doesn't exist."""
        if cls._client is None or cls._client.is_closed:
            logger.info("🚀 Initializing Global Sentinel HTTP Client...")
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(20.0, connect=10.0),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                follow_redirects=True
            )
        return cls._client

    @classmethod
    async def close_client(cls):
        """Cleanly close the global client. Use this during app shutdown."""
        if cls._client and not cls._client.is_closed:
            logger.info("🔌 Closing Global Sentinel HTTP Client...")
            await cls._client.aclose()
            cls._client = None

# Helper for easy access
async def get_http_client() -> httpx.AsyncClient:
    return await SentinelClient.get_client()
