"""Async HTTP client for BUVO QStream 2.0 ventilation fans."""

from datetime import datetime
from typing import Self
import aiohttp

from qstream.exceptions import (
    QStreamConnectionError,
    QStreamTimeoutError,
    QStreamResponseError,
)
from qstream.models import QStreamStatus
from qstream.parser import parse_status


class QStreamClient:
    """Async HTTP client for QStream 2.0 devices."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession | None = None,
        timeout: int = 10,
    ) -> None:
        """Initialize QStream client.

        Args:
            host: Device IP or hostname (e.g., "192.168.1.100")
            session: Optional aiohttp session (for connection pooling)
            timeout: Request timeout in seconds
        """
        # Normalize host URL
        if not host.startswith(("http://", "https://")):
            host = f"http://{host}"
        self._host = host.rstrip("/")

        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session = session
        self._owned_session = session is None

    async def close(self) -> None:
        """Close the client session if owned."""
        if self._owned_session and self._session:
            await self._session.close()

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args) -> None:
        """Async context manager exit."""
        await self.close()
