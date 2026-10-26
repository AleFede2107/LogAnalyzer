from dataclasses import dataclass, field


@dataclass
class Event:
    start_line: int
    header: str
    message_lines: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Diagnostic:
    line_number: int
    reason: str


@dataclass
class AnalysisResult:
    valid_event_count: int
    severity_counts: dict[str, int]
    malformed_event_count: int
    diagnostics: list[Diagnostic]
    is_empty_file: bool = False
