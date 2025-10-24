"""Pytest fixtures for QStream tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock
import aiohttp


def pytest_addoption(parser):
    """Add command line options for integration tests."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests against real device",
    )
    parser.addoption(
        "--device-ip",
        action="store",
        default=None,
        help="IP address of QStream device for integration tests",
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires real device)"
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless --run-integration is specified."""
    if config.getoption("--run-integration"):
        return
    skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture
def device_ip(request):
    """Get device IP from command line."""
    ip = request.config.getoption("--device-ip")
    if not ip:
        pytest.skip("--device-ip not specified")
    return ip


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
