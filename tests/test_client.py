"""Tests for QStream HTTP client."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
import aiohttp
from qstream.client import QStreamClient
from qstream.models import QStreamStatus, ScheduleMode
from qstream.exceptions import (
    QStreamConnectionError,
    QStreamTimeoutError,
    QStreamResponseError,
)


def test_client_init_with_host():
    """Client should initialize with host."""
    client = QStreamClient("192.168.1.100")
    assert client._host == "http://192.168.1.100"
    assert client._owned_session is True


def test_client_init_strips_trailing_slash():
    """Client should strip trailing slash from host."""
    client = QStreamClient("http://192.168.1.100/")
    assert client._host == "http://192.168.1.100"


def test_client_init_with_external_session():
    """Client should accept external session."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    client = QStreamClient("192.168.1.100", session=session)
    assert client._session is session
    assert client._owned_session is False


def test_client_init_with_timeout():
    """Client should accept custom timeout."""
    client = QStreamClient("192.168.1.100", timeout=30)
    assert client._timeout.total == 30


@pytest.mark.asyncio
async def test_get_status_success(mock_session, mock_response):
    """get_status should parse status response."""
    raw = "TIMER INACTIVE SCHEDULE OFF Qanalog 0% Qset 20% Qactual 20% DEMAND CONTROL ON DAY VALVE CLOSED"
    mock_session.get.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": raw}
    )

    client = QStreamClient("192.168.1.100", session=mock_session)
    status = await client.get_status()

    assert isinstance(status, QStreamStatus)
    assert status.set_flow == 20
    assert status.actual_flow == 20
    mock_session.get.assert_called_once_with(
        "http://192.168.1.100/Status", timeout=client._timeout
    )


@pytest.mark.asyncio
async def test_get_air_quality_success(mock_session, mock_response):
    """get_air_quality should return integer AQI value."""
    mock_session.get.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": "16"}
    )

    client = QStreamClient("192.168.1.100", session=mock_session)
    aqi = await client.get_air_quality()

    assert aqi == 16
    assert isinstance(aqi, int)


@pytest.mark.asyncio
async def test_get_nominal_flow_success(mock_session, mock_response):
    """get_nominal_flow should return percentage string."""
    mock_session.get.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": "70%"}
    )

    client = QStreamClient("192.168.1.100", session=mock_session)
    qnom = await client.get_nominal_flow()

    assert qnom == "70%"
    assert isinstance(qnom, str)


@pytest.mark.asyncio
async def test_get_datetime_success(mock_session, mock_response):
    """get_datetime should parse datetime string."""
    mock_session.get.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": "24/10/2025 23:19:05"}
    )

    client = QStreamClient("192.168.1.100", session=mock_session)
    dt = await client.get_datetime()

    assert isinstance(dt, datetime)
    assert dt.year == 2025
    assert dt.month == 10
    assert dt.day == 24
    assert dt.hour == 23
    assert dt.minute == 19
    assert dt.second == 5


@pytest.mark.asyncio
async def test_get_level_success(mock_session, mock_response):
    """get_level should return percentage as integer."""
    mock_session.get.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": "38%"}
    )

    client = QStreamClient("192.168.1.100", session=mock_session)
    level = await client.get_level(1)

    assert level == 38
    assert isinstance(level, int)
    mock_session.get.assert_called_once_with(
        "http://192.168.1.100/Levels?index=1", timeout=client._timeout
    )
