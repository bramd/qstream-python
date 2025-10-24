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

    async def _get_json(self, endpoint: str) -> dict:
        """Make GET request and return JSON response.

        Args:
            endpoint: API endpoint path (e.g., "/Status")

        Returns:
            JSON response as dictionary

        Raises:
            QStreamConnectionError: Cannot connect to device
            QStreamTimeoutError: Request timed out
            QStreamResponseError: Invalid response format
        """
        if not self._session:
            self._session = aiohttp.ClientSession()

        url = f"{self._host}{endpoint}"

        try:
            async with self._session.get(url, timeout=self._timeout) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientConnectionError as e:
            raise QStreamConnectionError(f"Cannot connect to {url}") from e
        except aiohttp.ClientResponseError as e:
            raise QStreamConnectionError(
                f"HTTP {e.status} error from {url}"
            ) from e
        except TimeoutError as e:
            raise QStreamTimeoutError(f"Request to {url} timed out") from e
        except Exception as e:
            raise QStreamResponseError(f"Unexpected error: {e}") from e

    async def get_status(self) -> QStreamStatus:
        """Get current device status.

        Returns:
            Parsed status object

        Raises:
            QStreamConnectionError: Cannot connect to device
            QStreamTimeoutError: Request timed out
            QStreamResponseError: Invalid response format
        """
        data = await self._get_json("/Status")
        raw_value = data.get("Value", "")
        return parse_status(raw_value)

    async def get_air_quality(self) -> int:
        """Get air quality index.

        Returns:
            Air quality index value

        Raises:
            QStreamConnectionError: Cannot connect to device
            QStreamTimeoutError: Request timed out
            QStreamResponseError: Invalid response format
        """
        data = await self._get_json("/AQI")
        try:
            return int(data.get("Value", "0"))
        except (ValueError, TypeError) as e:
            raise QStreamResponseError(
                f"Invalid AQI value: {data}", raw_response=str(data)
            ) from e

    async def get_nominal_flow(self) -> str:
        """Get nominal flow rate.

        Returns:
            Nominal flow rate as percentage string (e.g., "70%")

        Raises:
            QStreamConnectionError: Cannot connect to device
            QStreamTimeoutError: Request timed out
        """
        data = await self._get_json("/Qnom")
        return data.get("Value", "0%")

    async def get_datetime(self) -> datetime:
        """Get device date and time.

        Returns:
            Device datetime

        Raises:
            QStreamConnectionError: Cannot connect to device
            QStreamTimeoutError: Request timed out
            QStreamResponseError: Invalid datetime format
        """
        data = await self._get_json("/DateTime")
        dt_string = data.get("Value", "")
        try:
            return datetime.strptime(dt_string, "%d/%m/%Y %H:%M:%S")
        except ValueError as e:
            raise QStreamResponseError(
                f"Invalid datetime format: {dt_string}", raw_response=dt_string
            ) from e

    async def get_level(self, index: int) -> int:
        """Get preset level percentage.

        Args:
            index: Level index (1-4)

        Returns:
            Level percentage (0-100)

        Raises:
            QStreamConnectionError: Cannot connect to device
            QStreamTimeoutError: Request timed out
            QStreamResponseError: Invalid response format
        """
        data = await self._get_json(f"/Levels?index={index}")
        value_str = data.get("Value", "0%")
        try:
            return int(value_str.rstrip("%"))
        except ValueError as e:
            raise QStreamResponseError(
                f"Invalid level value: {value_str}", raw_response=value_str
            ) from e

    async def _post_json(self, endpoint: str, data: dict) -> dict:
        """Make POST request with JSON body.

        Args:
            endpoint: API endpoint path (e.g., "/Timer")
            data: JSON data to send

        Returns:
            JSON response as dictionary

        Raises:
            QStreamConnectionError: Cannot connect to device
            QStreamTimeoutError: Request timed out
            QStreamResponseError: Invalid response format
        """
        if not self._session:
            self._session = aiohttp.ClientSession()

        url = f"{self._host}{endpoint}"

        try:
            async with self._session.post(
                url, json=data, timeout=self._timeout
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientConnectionError as e:
            raise QStreamConnectionError(f"Cannot connect to {url}") from e
        except aiohttp.ClientResponseError as e:
            raise QStreamConnectionError(
                f"HTTP {e.status} error from {url}"
            ) from e
        except TimeoutError as e:
            raise QStreamTimeoutError(f"Request to {url} timed out") from e
        except Exception as e:
            raise QStreamResponseError(f"Unexpected error: {e}") from e

    async def set_timer(
        self,
        duration_minutes: int,
        speed_percentage: int,
        demand_control: bool = False,
    ) -> None:
        """Set timer with specified duration and speed.

        Args:
            duration_minutes: Timer duration (0 to cancel timer)
            speed_percentage: Fan speed percentage (0-100)
            demand_control: Enable demand control (responds to AQI)

        Raises:
            QStreamConnectionError: Cannot connect to device
            QStreamTimeoutError: Request timed out
        """
        demand = "ON" if demand_control else "OFF"
        # Mode doesn't matter for timer command, use NIGHT as default
        command = f"TIMER {duration_minutes} MIN {speed_percentage}% DEMAND CONTROL {demand} NIGHT"

        await self._post_json("/Timer", {"Value": command})

    async def cancel_timer(self) -> None:
        """Cancel active timer.

        Raises:
            QStreamConnectionError: Cannot connect to device
            QStreamTimeoutError: Request timed out
        """
        await self._post_json("/Timer", {"Value": "TIMER 0 MIN"})
