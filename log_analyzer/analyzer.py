from pathlib import Path

from .models import AnalysisResult, Diagnostic
from .parser import parse_events
from .validator import SEVERITIES, validate_event


def analyze_text(text: str) -> AnalysisResult:
    """Analyze log text and count only events that pass every validation."""
    if text == "":
        return AnalysisResult(
            valid_event_count=0,
            severity_counts={severity: 0 for severity in SEVERITIES},
            malformed_event_count=0,
            diagnostics=[],
            is_empty_file=True,
        )

    events, diagnostics = parse_events(text)
    severity_counts = {severity: 0 for severity in SEVERITIES}
    malformed_event_count = 0

    for event in events:
        severity, errors = validate_event(event)
        if errors:
            malformed_event_count += 1
            diagnostics.extend(
                Diagnostic(event.start_line, reason) for reason in errors
            )
        else:
            severity_counts[severity] += 1

    return AnalysisResult(
        valid_event_count=sum(severity_counts.values()),
        severity_counts=severity_counts,
        malformed_event_count=malformed_event_count,
        diagnostics=diagnostics,
    )


def analyze_file(path: str | Path) -> AnalysisResult:
    """Read a UTF-8 log file and analyze its contents."""
    text = Path(path).read_text(encoding="utf-8")
    return analyze_text(text)
