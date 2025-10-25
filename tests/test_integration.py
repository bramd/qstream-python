"""Integration tests against real QStream device.

These tests require a real device and are skipped by default.
Run with: pytest tests/test_integration.py --run-integration --device-ip=192.168.1.100
"""

import pytest
from qstream import QStreamClient, QStreamStatus


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_status_real_device(device_ip):
    """Test get_status against real device."""
    async with QStreamClient(device_ip) as client:
        status = await client.get_status()

        assert isinstance(status, QStreamStatus)
        assert 0 <= status.analog_flow <= 100
        assert 0 <= status.set_flow <= 100
        assert 0 <= status.actual_flow <= 100
        print(f"\nDevice status: {status.raw_value}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_air_quality_real_device(device_ip):
    """Test get_air_quality against real device."""
    async with QStreamClient(device_ip) as client:
        aqi = await client.get_air_quality()

        assert isinstance(aqi, int)
        assert aqi >= 0
        print(f"\nAir quality index: {aqi}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_levels_real_device(device_ip):
    """Test get_level for all preset levels (0-4)."""
    async with QStreamClient(device_ip) as client:
        levels = {}
        for i in range(0, 5):
            level = await client.get_level(i)
            assert isinstance(level, int)
            assert 0 <= level <= 100
            levels[i] = level

        print(f"\nPreset levels: {levels}")
