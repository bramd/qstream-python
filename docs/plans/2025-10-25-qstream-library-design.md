# QStream Python Library - Design Document

**Date:** 2025-10-25
**Status:** Initial Design
**Target:** Home Assistant Integration

## Overview

An async Python library for controlling BUVO QStream 2.0 WiFi-enabled ventilation fans via their HTTP API. The library provides a thin async wrapper around the undocumented HTTP endpoints, returning typed Python objects for easy integration with Home Assistant and other automation systems.

## Design Principles

1. **Thin async wrapper** - Minimal abstraction over HTTP API, no state management
2. **Typed responses** - Return dataclasses with proper type hints, not raw JSON
3. **Home Assistant compatibility** - Accept external aiohttp sessions for connection pooling
4. **Simple error handling** - Custom exceptions wrapping aiohttp errors
5. **YAGNI** - Only implement proven, tested endpoints

## Architecture

### Project Structure

```
qstream-py/
├── pyproject.toml
├── README.md
├── AGENTS.md                # AI assistant development guide
├── .gitignore
├── docs/
│   └── plans/               # Design documents
├── src/
│   └── qstream/
│       ├── __init__.py      # Public API exports
│       ├── client.py        # QStreamClient class
│       ├── models.py        # Response data models
│       ├── exceptions.py    # Custom exceptions
│       └── const.py         # Constants (endpoints, defaults)
└── tests/
    ├── __init__.py
    ├── test_client.py       # Client tests
    ├── test_models.py       # Model parsing tests
    └── conftest.py          # pytest fixtures
```

### Core Components

#### 1. Client Class (`client.py`)

```python
class QStreamClient:
    """Async HTTP client for BUVO QStream 2.0 ventilation fans."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession | None = None,
        timeout: int = 10
    ):
        """
        Args:
            host: Device IP or hostname (e.g., "192.168.1.100")
            session: Optional aiohttp session (for connection pooling)
            timeout: Request timeout in seconds
        """

    # Read Operations
    async def get_status() -> QStreamStatus
    async def get_air_quality() -> int
    async def get_nominal_flow() -> str
    async def get_datetime() -> datetime
    async def get_level(index: int) -> int  # index 1-4

    # Write Operations
    async def set_timer(
        duration_minutes: int,
        speed_percentage: int,
        demand_control: bool = False
    ) -> None

    async def cancel_timer() -> None

    # Lifecycle
    async def close() -> None
    async def __aenter__(self) -> Self
    async def __aexit__(self, *args) -> None
```

#### 2. Data Models (`models.py`)

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ScheduleMode(str, Enum):
    """Schedule mode based on time of day."""
    DAY = "DAY"
    NIGHT = "NIGHT"

@dataclass
class QStreamStatus:
    """Parsed status from /Status endpoint."""

    # Timer state
    timer_active: bool
    timer_remaining_minutes: int | None

    # Schedule state
    schedule_enabled: bool
    schedule_remaining_minutes: int | None
    schedule_mode: ScheduleMode | None  # None when schedule is OFF

    # Flow measurements
    analog_flow: int          # percentage (0-100)
    set_flow: int             # percentage (0-100)
    actual_flow: int          # percentage (0-100)

    # Control state
    demand_control_enabled: bool  # Responds to AQI sensor
    valve_open: bool              # True=OPEN, False=CLOSED

    # Raw data for debugging
    raw_value: str
```

**Parsing Logic:**
- Input: `"TIMER ACTIVE 2 MIN Qanalog 0% Qset 38% Qactual 38% DEMAND CONTROL OFF DAY VALVE CLOSED"`
- Parse using string splitting and regex for percentages
- `schedule_mode` is None when `schedule_enabled` is False
- `timer_remaining_minutes` is None when `timer_active` is False

#### 3. Exceptions (`exceptions.py`)

```python
class QStreamError(Exception):
    """Base exception for all QStream errors."""

class QStreamConnectionError(QStreamError):
    """Cannot connect to device (network/host unreachable)."""

class QStreamTimeoutError(QStreamError):
    """Request timed out."""

class QStreamResponseError(QStreamError):
    """Unexpected or invalid response format."""

    def __init__(self, message: str, raw_response: str | None = None):
        super().__init__(message)
        self.raw_response = raw_response
```

## API Endpoints

### Discovered Endpoints

| Endpoint | Method | Description | Response Format |
|----------|--------|-------------|-----------------|
| `/Status` | GET | Complete device status | JSON with complex string value |
| `/AQI` | GET | Air Quality Index | JSON: `{"Value": "16"}` |
| `/Qnom` | GET | Nominal flow rate | JSON: `{"Value": "70%"}` |
| `/DateTime` | GET | Device date/time | JSON: `{"Value": "24/10/2025 23:19:05"}` |
| `/Levels?index=N` | GET | Preset level (1-4) | JSON: `{"Value": "38%"}` |
| `/Timer` | GET | Timer remaining minutes | JSON: `{"Value": "5"}` |
| `/Timer` | POST | Set/cancel timer | JSON body required |

### Timer Control Details

**Set Timer:**
```json
POST /Timer
Content-Type: application/json

{
  "Value": "TIMER 30 MIN 50% DEMAND CONTROL OFF NIGHT"
}
```

**Cancel Timer:**
```json
POST /Timer
Content-Type: application/json

{
  "Value": "TIMER 0 MIN"
}
```

**Behavior:**
- Setting timer duration to 0 cancels the timer
- When timer is cancelled, fan reverts to previous settings
- Timer overrides demand control during its duration

## Testing Strategy

### Unit Tests
- Mock aiohttp responses
- Test status string parsing with various inputs
- Test error handling and exception wrapping
- Test session lifecycle (owned vs. external)

### Integration Tests
- Optional flag to test against real device
- **Important:** Always ask user for device IP before running
- Test read operations (safe, non-destructive)
- Test timer control (requires user permission)
- Verify parsing against actual device responses

### Test Coverage
- Focus on `QStreamStatus` parsing (most complex, error-prone)
- Verify all enum values are handled
- Test edge cases (missing fields, unexpected values)

## Dependencies

```toml
[project]
name = "qstream"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "aiohttp>=3.9.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-aiohttp>=1.0.0",
    "pytest-cov>=4.0.0",
]
```

**Python Version:** 3.11+ required for modern type syntax (`int | None`)

## Future Enhancements (Out of Scope for v1)

- Auto-discovery of devices on local network
- Device metadata (name, MAC address, firmware version)
- Schedule management endpoints (low priority - use Home Assistant automations)
- Set level convenience method: `async def set_level(index: int, duration_minutes: int = 0)`
- Verify if `demand_control` parameter in `set_timer()` actually works
- Explore additional undocumented endpoints

## Open Questions

1. ✅ **Timer cancellation** - Confirmed: `POST /Timer` with `{"Value":"TIMER 0 MIN"}`
2. ⏳ **Demand control in timer** - Need to verify if demand_control parameter in set_timer() works
3. ⏳ **Device info endpoints** - Explore `/DeviceInfo`, `/Version`, `/Name` for metadata
4. ⏳ **Schedule control** - Find endpoints to enable/disable schedule (if needed)

## Implementation Notes

### Connection Management
- Support both managed (`async with QStreamClient(...)`) and manual lifecycle
- Only close session if client created it (respect external sessions)
- Home Assistant pattern: pass shared session for connection pooling

### Error Handling Pattern
- Wrap all `aiohttp.ClientError` → `QStreamConnectionError`
- Wrap all `asyncio.TimeoutError` → `QStreamTimeoutError`
- Invalid response parsing → `QStreamResponseError` with raw data preserved

### Type Safety
- Full type annotations throughout
- Use `str` Enum for JSON serialization compatibility
- Use `| None` for optional fields (Python 3.11+ syntax)

## Example Usage

```python
import asyncio
from qstream import QStreamClient

async def main():
    # Managed lifecycle
    async with QStreamClient("192.168.1.100") as client:
        status = await client.get_status()
        print(f"Current speed: {status.actual_flow}%")
        print(f"Timer active: {status.timer_active}")

        # Set timer for 30 minutes at 75%
        await client.set_timer(duration_minutes=30, speed_percentage=75)

        # Check air quality
        aqi = await client.get_air_quality()
        print(f"Air quality index: {aqi}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Git Setup

- Initialize git repository in project root
- Standard Python .gitignore (venv, __pycache__, .pytest_cache, *.pyc, etc.)
- Initial commit with project structure before implementation

## Package Manager

Use **uv** for all package management:
- `uv init` - Initialize project
- `uv add <package>` - Add dependencies
- `uv sync` - Install dependencies
- `uv run pytest` - Run tests
