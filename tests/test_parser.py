"""Tests for status string parsing."""

import pytest
from qstream.parser import parse_status
from qstream.models import ScheduleMode
from qstream.exceptions import QStreamResponseError


def test_parse_status_timer_active():
    """Should parse status with active timer."""
    raw = "TIMER ACTIVE 2 MIN Qanalog 0% Qset 38% Qactual 38% DEMAND CONTROL OFF DAY VALVE CLOSED"
    status = parse_status(raw)

    assert status.timer_active is True
    assert status.timer_remaining_minutes == 2
    assert status.schedule_enabled is False
    assert status.schedule_mode is None
    assert status.analog_flow == 0
    assert status.set_flow == 38
    assert status.actual_flow == 38
    assert status.demand_control_enabled is False
    assert status.valve_open is False
    assert status.raw_value == raw


def test_parse_status_schedule_active():
    """Should parse status with active schedule."""
    raw = "TIMER INACTIVE SCHEDULE ON 25 MIN Qanalog 0% Qset 28% Qactual 28% DEMAND CONTROL ON NIGHT VALVE CLOSED"
    status = parse_status(raw)

    assert status.timer_active is False
    assert status.timer_remaining_minutes is None
    assert status.schedule_enabled is True
    assert status.schedule_remaining_minutes == 25
    assert status.schedule_mode == ScheduleMode.NIGHT
    assert status.demand_control_enabled is True


def test_parse_status_basic():
    """Should parse basic status with no timer or schedule."""
    raw = "TIMER INACTIVE SCHEDULE OFF Qanalog 0% Qset 20% Qactual 20% DEMAND CONTROL ON DAY VALVE CLOSED"
    status = parse_status(raw)

    assert status.timer_active is False
    assert status.timer_remaining_minutes is None
    assert status.schedule_enabled is False
    assert status.schedule_remaining_minutes is None
    assert status.schedule_mode is None
    assert status.analog_flow == 0
    assert status.set_flow == 20
    assert status.actual_flow == 20
    assert status.demand_control_enabled is True
    assert status.valve_open is False


def test_parse_status_valve_open():
    """Should parse status with valve open."""
    raw = "TIMER INACTIVE SCHEDULE OFF Qanalog 0% Qset 20% Qactual 20% DEMAND CONTROL ON DAY VALVE OPEN"
    status = parse_status(raw)

    assert status.valve_open is True


def test_parse_status_invalid_format():
    """Should raise QStreamResponseError for invalid format."""
    raw = "INVALID STATUS STRING"

    with pytest.raises(QStreamResponseError) as exc_info:
        parse_status(raw)

    assert "Missing required flow values" in str(exc_info.value)
    assert exc_info.value.raw_response == raw
