# QStream Python Library - AI Development Guide

## Project Overview
Async Python library for BUVA QStream 2.0 ventilation fan control via HTTP API.
Target use case: Home Assistant integration.

## Key Constraints
- No official API docs - endpoints discovered via reverse engineering
- Use uv as package manager
- Python 3.11+ with full type hints
- Thin async wrapper pattern (no state management)

## Testing Against Real Device
- A real QStream 2.0 device may be available on the local network
- **Always ask the user** if a real device is available and get the IP address before testing
- Get user permission before sending any control commands (only read operations without permission)
- Status parsing is critical - verify against actual responses when possible

## API Endpoints Discovered
See docs/plans/ for complete endpoint documentation

## Development Commands
- `uv sync` - Install dependencies
- `uv run pytest` - Run tests
- `uv run pytest --cov=qstream --cov-report=html` - Run tests with coverage
