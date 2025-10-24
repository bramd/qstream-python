"""Parser for QStream API response strings."""

import re
from qstream.models import QStreamStatus, ScheduleMode
from qstream.exceptions import QStreamResponseError


def parse_status(raw_value: str) -> QStreamStatus:
    """Parse status string from /Status endpoint.

    Args:
        raw_value: Raw status string from device

    Returns:
        Parsed QStreamStatus object

    Raises:
        QStreamResponseError: If status string format is invalid
    """
    try:
        # Parse timer state
        timer_active = "TIMER ACTIVE" in raw_value
        timer_match = re.search(r"TIMER ACTIVE (\d+) MIN", raw_value)
        timer_remaining_minutes = int(timer_match.group(1)) if timer_match else None

        # Parse schedule state
        schedule_enabled = "SCHEDULE ON" in raw_value
        schedule_match = re.search(r"SCHEDULE ON (\d+) MIN", raw_value)
        schedule_remaining_minutes = (
            int(schedule_match.group(1)) if schedule_match else None
        )

        # Parse schedule mode (only if schedule enabled)
        schedule_mode = None
        if schedule_enabled:
            if "DAY" in raw_value:
                schedule_mode = ScheduleMode.DAY
            elif "NIGHT" in raw_value:
                schedule_mode = ScheduleMode.NIGHT

        # Parse flow percentages
        analog_match = re.search(r"Qanalog (\d+)%", raw_value)
        set_match = re.search(r"Qset (\d+)%", raw_value)
        actual_match = re.search(r"Qactual (\d+)%", raw_value)

        if not all([analog_match, set_match, actual_match]):
            raise QStreamResponseError(
                "Missing required flow values", raw_response=raw_value
            )

        analog_flow = int(analog_match.group(1))
        set_flow = int(set_match.group(1))
        actual_flow = int(actual_match.group(1))

        # Parse demand control
        demand_control_enabled = "DEMAND CONTROL ON" in raw_value

        # Parse valve state
        valve_open = "VALVE OPEN" in raw_value

        return QStreamStatus(
            timer_active=timer_active,
            timer_remaining_minutes=timer_remaining_minutes,
            schedule_enabled=schedule_enabled,
            schedule_remaining_minutes=schedule_remaining_minutes,
            schedule_mode=schedule_mode,
            analog_flow=analog_flow,
            set_flow=set_flow,
            actual_flow=actual_flow,
            demand_control_enabled=demand_control_enabled,
            valve_open=valve_open,
            raw_value=raw_value,
        )
    except (AttributeError, ValueError) as e:
        raise QStreamResponseError(
            f"Failed to parse status string: {e}", raw_response=raw_value
        ) from e
