"""Tests for QStream data models."""

import pytest
from qstream.models import ScheduleMode, QStreamStatus


def test_schedule_mode_enum_values():
    """ScheduleMode should have DAY and NIGHT values."""
    assert ScheduleMode.DAY == "DAY"
    assert ScheduleMode.NIGHT == "NIGHT"


def test_schedule_mode_is_string():
    """ScheduleMode values should be strings for JSON compatibility."""
    assert isinstance(ScheduleMode.DAY.value, str)
    assert isinstance(ScheduleMode.NIGHT.value, str)


def test_qstream_status_dataclass_creation():
    """QStreamStatus should be creatable with all fields."""
    status = QStreamStatus(
        timer_active=True,
        timer_remaining_minutes=5,
        schedule_enabled=False,
        schedule_remaining_minutes=None,
        schedule_mode=None,
        analog_flow=0,
        set_flow=50,
        actual_flow=50,
        demand_control_enabled=False,
        valve_open=False,
        raw_value="TIMER ACTIVE 5 MIN Qanalog 0% Qset 50% Qactual 50% DEMAND CONTROL OFF NIGHT VALVE CLOSED",
    )

    assert status.timer_active is True
    assert status.timer_remaining_minutes == 5
    assert status.schedule_enabled is False
    assert status.schedule_remaining_minutes is None
    assert status.schedule_mode is None
    assert status.analog_flow == 0
    assert status.set_flow == 50
    assert status.actual_flow == 50
    assert status.demand_control_enabled is False
    assert status.valve_open is False
    assert "TIMER ACTIVE" in status.raw_value


def test_qstream_status_with_schedule_mode():
    """QStreamStatus should support schedule_mode when schedule is enabled."""
    status = QStreamStatus(
        timer_active=False,
        timer_remaining_minutes=None,
        schedule_enabled=True,
        schedule_remaining_minutes=25,
        schedule_mode=ScheduleMode.NIGHT,
        analog_flow=0,
        set_flow=28,
        actual_flow=28,
        demand_control_enabled=True,
        valve_open=False,
        raw_value="TIMER INACTIVE SCHEDULE ON 25 MIN Qanalog 0% Qset 28% Qactual 28% DEMAND CONTROL ON NIGHT VALVE CLOSED",
    )

    assert status.schedule_enabled is True
    assert status.schedule_mode == ScheduleMode.NIGHT
    assert status.schedule_remaining_minutes == 25
