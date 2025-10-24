# QStream Python Library

Async Python library for controlling BUVA QStream 2.0 WiFi-enabled ventilation fans via their HTTP API.

## Features

- Fully async API using aiohttp
- Type-safe responses with dataclasses
- Home Assistant compatible (external session support)
- Complete error handling
- Python 3.11+ with full type hints

## Installation

Using uv:
```bash
uv add qstream
```

Using pip:
```bash
pip install qstream
```

## Quick Start

```python
import asyncio
from qstream import QStreamClient

async def main():
    async with QStreamClient("192.168.1.100") as client:
        # Get current status
        status = await client.get_status()
        print(f"Current speed: {status.actual_flow}%")
        print(f"Timer active: {status.timer_active}")

        # Check air quality
        aqi = await client.get_air_quality()
        print(f"Air quality index: {aqi}")

        # Set timer for 30 minutes at 75%
        await client.set_timer(duration_minutes=30, speed_percentage=75)

        # Cancel timer
        await client.cancel_timer()

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### QStreamClient

#### Initialization

```python
client = QStreamClient(
    host="192.168.1.100",      # Device IP or hostname
    session=None,               # Optional aiohttp session
    timeout=10                  # Request timeout in seconds
)
```

#### Read Operations

- `await client.get_status()` -> `QStreamStatus` - Complete device status
- `await client.get_air_quality()` -> `int` - Air quality index
- `await client.get_nominal_flow()` -> `str` - Nominal flow rate (e.g., "70%")
- `await client.get_datetime()` -> `datetime` - Device date/time
- `await client.get_level(index)` -> `int` - Preset level percentage (index 1-4)

#### Write Operations

- `await client.set_timer(duration_minutes, speed_percentage, demand_control=False)` - Set timer
- `await client.cancel_timer()` - Cancel active timer

### QStreamStatus

Dataclass containing parsed device status:

```python
@dataclass
class QStreamStatus:
    timer_active: bool
    timer_remaining_minutes: int | None
    schedule_enabled: bool
    schedule_remaining_minutes: int | None
    schedule_mode: ScheduleMode | None  # DAY or NIGHT
    analog_flow: int                     # 0-100
    set_flow: int                        # 0-100
    actual_flow: int                     # 0-100
    demand_control_enabled: bool
    valve_open: bool
    raw_value: str
```

### Exceptions

- `QStreamError` - Base exception
- `QStreamConnectionError` - Cannot connect to device
- `QStreamTimeoutError` - Request timed out
- `QStreamResponseError` - Invalid response format

## Home Assistant Integration

```python
import aiohttp
from qstream import QStreamClient

# Share session with Home Assistant
async with aiohttp.ClientSession() as session:
    client = QStreamClient("192.168.1.100", session=session)
    status = await client.get_status()
```

## Development

```bash
# Clone repository
git clone <repo-url>
cd qstream

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=qstream --cov-report=html
```

## License

MIT

## Credits

This library is not officially affiliated with BUVA. The API endpoints were discovered through community reverse engineering efforts.
