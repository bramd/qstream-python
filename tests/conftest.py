"""Pytest fixtures for QStream tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock
import aiohttp


@pytest.fixture
def mock_response():
    """Create a mock aiohttp response."""

    def _mock_response(json_data=None, status=200):
        response = AsyncMock(spec=aiohttp.ClientResponse)
        response.status = status
        response.json = AsyncMock(return_value=json_data)
        return response

    return _mock_response


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    return session
