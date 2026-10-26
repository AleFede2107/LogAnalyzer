import re
from datetime import date

from .models import Diagnostic, Event

DATE_AT_START = re.compile(
    r"^(?P<date>[0-9]{2}/[0-9]{2}/[0-9]{2})(?=\s|$)"
)
DATE_LIKE_AT_START = re.compile(
    r"^(?P<date>(?:[0-9]{1,2}[./-]){2}[0-9]{1,4}"
    r"|[0-9]{4}-[0-9]{1,2}-[0-9]{1,2})(?=\s|$)"
)


def _is_real_date(date_text: str) -> bool:
    """Check the calendar date after mapping YY into the 2000s."""
    day, month, year = (int(part) for part in date_text.split("/"))
    try:
        date(2000 + year, month, day)
    except ValueError:
        return False
    return True


def parse_events(text: str) -> tuple[list[Event], list[Diagnostic]]:
    """Group lines by valid date boundaries and normalize attached blank lines."""
    events: list[Event] = []
    diagnostics: list[Diagnostic] = []
    current_event: Event | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            if current_event is None:
                diagnostics.append(
                    Diagnostic(line_number, "blank line has no preceding event")
                )
            else:
                current_event.message_lines.append("all clear")
            continue

        date_match = DATE_AT_START.match(line)
        if date_match:
            date_text = date_match.group("date")
            if not _is_real_date(date_text):
                diagnostics.append(
                    Diagnostic(line_number, f"invalid calendar date {date_text!r}")
                )
                if current_event is not None:
                    current_event.message_lines.append(line)
                continue

            # A valid date at column one is a boundary, even if the rest is malformed.
            current_event = Event(start_line=line_number, header=line)
            events.append(current_event)
            continue

        date_like_match = DATE_LIKE_AT_START.match(line)
        if date_like_match:
            date_text = date_like_match.group("date")
            diagnostics.append(
                Diagnostic(
                    line_number,
                    f"date {date_text!r} must use DD/MM/YY",
                )
            )
            if current_event is not None:
                current_event.message_lines.append(line)
            continue

        if current_event is None:
            diagnostics.append(
                Diagnostic(line_number, "text appears before the first event")
            )
        else:
            current_event.message_lines.append(line)

    return events, diagnostics
