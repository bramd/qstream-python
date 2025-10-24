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


@pytest.mark.asyncio
async def test_set_timer_success(mock_session, mock_response):
    """set_timer should post timer command."""
    mock_session.post.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": "TIMER 30 MIN 50% DEMAND CONTROL OFF NIGHT"}
    )

    client = QStreamClient("192.168.1.100", session=mock_session)
    await client.set_timer(duration_minutes=30, speed_percentage=50)

    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert call_args[0][0] == "http://192.168.1.100/Timer"
    assert "TIMER 30 MIN 50%" in call_args[1]["json"]["Value"]
    assert "DEMAND CONTROL OFF" in call_args[1]["json"]["Value"]


@pytest.mark.asyncio
async def test_set_timer_with_demand_control(mock_session, mock_response):
    """set_timer should support demand control parameter."""
    mock_session.post.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": "TIMER 15 MIN 75% DEMAND CONTROL ON NIGHT"}
    )

    client = QStreamClient("192.168.1.100", session=mock_session)
    await client.set_timer(
        duration_minutes=15, speed_percentage=75, demand_control=True
    )

    call_args = mock_session.post.call_args
    assert "DEMAND CONTROL ON" in call_args[1]["json"]["Value"]


@pytest.mark.asyncio
async def test_cancel_timer_success(mock_session, mock_response):
    """cancel_timer should post timer 0 command."""
    mock_session.post.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": "TIMER 0 MIN"}
    )

    client = QStreamClient("192.168.1.100", session=mock_session)
    await client.cancel_timer()

    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert call_args[0][0] == "http://192.168.1.100/Timer"
    assert call_args[1]["json"]["Value"] == "TIMER 0 MIN"


@pytest.mark.asyncio
async def test_get_status_connection_error(mock_session):
    """Should raise QStreamConnectionError on connection failure."""
    mock_session.get.side_effect = aiohttp.ClientConnectionError("Connection failed")

    client = QStreamClient("192.168.1.100", session=mock_session)

    with pytest.raises(QStreamConnectionError) as exc_info:
        await client.get_status()

    assert "Cannot connect" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_status_timeout_error(mock_session):
    """Should raise QStreamTimeoutError on timeout."""
    mock_session.get.side_effect = TimeoutError("Request timeout")

    client = QStreamClient("192.168.1.100", session=mock_session)

    with pytest.raises(QStreamTimeoutError) as exc_info:
        await client.get_status()

    assert "timed out" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_status_invalid_json(mock_session, mock_response):
    """Should raise QStreamResponseError on invalid status format."""
    mock_session.get.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": "INVALID FORMAT"}
    )

    client = QStreamClient("192.168.1.100", session=mock_session)

    with pytest.raises(QStreamResponseError) as exc_info:
        await client.get_status()

    assert exc_info.value.raw_response == "INVALID FORMAT"


@pytest.mark.asyncio
async def test_context_manager(mock_session, mock_response):
    """Client should work as async context manager."""
    raw = "TIMER INACTIVE SCHEDULE OFF Qanalog 0% Qset 20% Qactual 20% DEMAND CONTROL ON DAY VALVE CLOSED"
    mock_session.get.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": raw}
    )
    mock_session.close = AsyncMock()

    async with QStreamClient("192.168.1.100", session=mock_session) as client:
        status = await client.get_status()
        assert status.set_flow == 20

    # Session should not be closed (not owned)
    mock_session.close.assert_not_called()


@pytest.mark.asyncio
async def test_context_manager_owned_session():
    """Client should close owned session on exit."""
    client = QStreamClient("192.168.1.100")

    async with client:
        # Create session manually for testing
        client._session = AsyncMock(spec=aiohttp.ClientSession)
        client._session.close = AsyncMock()

    # Owned session should be closed
    client._session.close.assert_called_once()


@pytest.mark.asyncio
async def test_close_no_session():
    """Client.close should handle case with no session."""
    client = QStreamClient("192.168.1.100")
    await client.close()  # Should not raise


@pytest.mark.asyncio
async def test_get_status_http_error(mock_session):
    """Should raise QStreamConnectionError on HTTP error."""
    error = aiohttp.ClientResponseError(
        request_info=None,
        history=None,
        status=404
    )
    mock_session.get.side_effect = error

    client = QStreamClient("192.168.1.100", session=mock_session)

    with pytest.raises(QStreamConnectionError) as exc_info:
        await client.get_status()

    assert "HTTP 404" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_status_unexpected_error(mock_session):
    """Should raise QStreamResponseError on unexpected error."""
    mock_session.get.side_effect = ValueError("Unexpected issue")

    client = QStreamClient("192.168.1.100", session=mock_session)

    with pytest.raises(QStreamResponseError) as exc_info:
        await client.get_status()

    assert "Unexpected error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_air_quality_invalid_value(mock_session, mock_response):
    """Should raise QStreamResponseError on invalid AQI value."""
    mock_session.get.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": "not_a_number"}
    )

    client = QStreamClient("192.168.1.100", session=mock_session)

    with pytest.raises(QStreamResponseError) as exc_info:
        await client.get_air_quality()

    assert "Invalid AQI value" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_datetime_invalid_format(mock_session, mock_response):
    """Should raise QStreamResponseError on invalid datetime format."""
    mock_session.get.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": "not a valid datetime"}
    )

    client = QStreamClient("192.168.1.100", session=mock_session)

    with pytest.raises(QStreamResponseError) as exc_info:
        await client.get_datetime()

    assert "Invalid datetime format" in str(exc_info.value)
    assert exc_info.value.raw_response == "not a valid datetime"


@pytest.mark.asyncio
async def test_get_level_invalid_value(mock_session, mock_response):
    """Should raise QStreamResponseError on invalid level value."""
    mock_session.get.return_value.__aenter__.return_value = mock_response(
        json_data={"Value": "invalid%"}
    )

    client = QStreamClient("192.168.1.100", session=mock_session)

    with pytest.raises(QStreamResponseError) as exc_info:
        await client.get_level(1)

    assert "Invalid level value" in str(exc_info.value)
    assert exc_info.value.raw_response == "invalid%"


@pytest.mark.asyncio
async def test_set_timer_connection_error(mock_session):
    """Should raise QStreamConnectionError on POST connection failure."""
    mock_session.post.side_effect = aiohttp.ClientConnectionError("Connection failed")

    client = QStreamClient("192.168.1.100", session=mock_session)

    with pytest.raises(QStreamConnectionError) as exc_info:
        await client.set_timer(30, 50)

    assert "Cannot connect" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_timer_http_error(mock_session):
    """Should raise QStreamConnectionError on POST HTTP error."""
    error = aiohttp.ClientResponseError(
        request_info=None,
        history=None,
        status=500
    )
    mock_session.post.side_effect = error

    client = QStreamClient("192.168.1.100", session=mock_session)

    with pytest.raises(QStreamConnectionError) as exc_info:
        await client.set_timer(30, 50)

    assert "HTTP 500" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_timer_timeout(mock_session):
    """Should raise QStreamTimeoutError on POST timeout."""
    mock_session.post.side_effect = TimeoutError("Request timeout")

    client = QStreamClient("192.168.1.100", session=mock_session)

    with pytest.raises(QStreamTimeoutError) as exc_info:
        await client.set_timer(30, 50)

    assert "timed out" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_timer_unexpected_error(mock_session):
    """Should raise QStreamResponseError on POST unexpected error."""
    mock_session.post.side_effect = ValueError("Unexpected issue")

    client = QStreamClient("192.168.1.100", session=mock_session)

    with pytest.raises(QStreamResponseError) as exc_info:
        await client.set_timer(30, 50)

    assert "Unexpected error" in str(exc_info.value)
