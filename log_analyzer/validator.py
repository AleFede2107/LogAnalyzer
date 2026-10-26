import re
from datetime import time

from .models import Event

SEVERITIES = ("INFO", "WARNING", "ERROR")
HEADER_PATTERN = re.compile(
    r"^(?P<date>[0-9]{2}/[0-9]{2}/[0-9]{2})"
    r"(?:\s+(?P<time>\S+))?"
    r"(?:\s+\[(?P<severity>[^\]]*)\])?"
    r"(?:\s+(?P<message>.*))?$"
)
TIME_PATTERN = re.compile(r"^[0-9]{2}:[0-9]{2}$")


def validate_event(event: Event) -> tuple[str | None, list[str]]:
    """Return the valid severity, if any, and all event-level validation errors."""
    errors: list[str] = []
    match = HEADER_PATTERN.fullmatch(event.header)
    if match is None:
        return None, ["header does not match DD/MM/YY HH:MM [SEVERITY] Message"]

    time_text = match.group("time")
    if time_text is None:
        errors.append("time is missing")
    elif TIME_PATTERN.fullmatch(time_text) is None:
        errors.append(f"time {time_text!r} must use HH:MM")
    else:
        hour, minute = (int(part) for part in time_text.split(":"))
        try:
            time(hour, minute)
        except ValueError:
            errors.append(f"time {time_text!r} is not a real 24-hour time")

    severity = match.group("severity")
    if severity is None:
        errors.append("severity is missing or not enclosed in brackets")
    elif severity not in SEVERITIES:
        errors.append(
            f"severity {severity!r} is invalid; use INFO, WARNING, or ERROR"
        )

    message_parts = [match.group("message") or "", *event.message_lines]
    if not "\n".join(message_parts).strip():
        errors.append("message is empty or contains only whitespace")

    if errors:
        return None, errors
    return severity, []
