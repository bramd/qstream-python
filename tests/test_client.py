"""Tests for QStream HTTP client."""

import pytest
from unittest.mock import AsyncMock, patch
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
