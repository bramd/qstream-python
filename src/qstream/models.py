"""Data models for QStream API responses."""

from dataclasses import dataclass
from enum import Enum


class ScheduleMode(str, Enum):
    """Schedule mode based on time of day."""

    DAY = "DAY"
    NIGHT = "NIGHT"


@dataclass
class QStreamStatus:
    """Parsed status from /Status endpoint.

    Attributes:
        timer_active: Whether timer is currently running
        timer_remaining_minutes: Minutes remaining on timer (None if inactive)
        schedule_enabled: Whether schedule is enabled
        schedule_remaining_minutes: Minutes until next schedule event (None if disabled)
        schedule_mode: DAY or NIGHT mode (None if schedule disabled)
        analog_flow: Analog flow percentage (0-100)
        set_flow: Target flow percentage (0-100)
        actual_flow: Actual flow percentage (0-100)
        demand_control_enabled: Whether responding to AQI sensor
        valve_open: True if valve is open, False if closed
        raw_value: Original response string for debugging
    """

    timer_active: bool
    timer_remaining_minutes: int | None
    schedule_enabled: bool
    schedule_remaining_minutes: int | None
    schedule_mode: ScheduleMode | None
    analog_flow: int
    set_flow: int
    actual_flow: int
    demand_control_enabled: bool
    valve_open: bool
    raw_value: str
