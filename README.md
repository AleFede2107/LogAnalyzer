# Console Log Analyzer

A standard-library Python console program for validating and counting log events.

## Run it

From this folder, run:

```text
python -m log_analyzer
```

Enter the path to a UTF-8 text file when prompted. The analyzer reports valid
event totals, counts for `INFO`, `WARNING`, and `ERROR`, malformed-event count,
and diagnostics with source line numbers.

Run the tests with:

```text
python -m unittest discover -s tests -v
```

## Confirmed validation rules

- Header format: `DD/MM/YY HH:MM [SEVERITY] Message`.
- `HH:MM` is a 24-hour time; seconds are not accepted.
- `YY` maps to 2000–2099.
- Only uppercase `INFO`, `WARNING`, and `ERROR` are accepted.
- A calendar-valid date at the start of a line starts an event, even if the
  remaining header is invalid. Date-shaped but impossible dates and dates in a
  different format are diagnosed but do not start an event; if an event is
  already open, that line is treated as its message continuation.
- Nonblank lines continue the current event unless they start a new event.
  Text before the first event is diagnosed as preamble.
- A blank line after an event adds `all clear` at that position in its message.
  A leading blank line is diagnosed because there is no preceding event.
- Message-edge whitespace is trimmed for validation, and at least one
  non-whitespace character is required. Messages have no length limit.
- Malformed-event count counts only events that started with a calendar-valid
  date and then failed event validation. Preamble, invalid-date lines, and
  unattached leading blanks receive diagnostics but are not events and do not
  increase that count.
- `ERROR` is an application severity. It is counted as a valid event when the
  rest of the event is valid; it is not itself a validation failure.

## Project responsibilities

- `log_analyzer/parser.py`: `parse_events` groups physical lines into events,
  inserts `all clear` for attached blank lines, and reports input outside
  events. `_is_real_date` applies the confirmed century rule and checks actual
  calendar validity.
- `log_analyzer/validator.py`: `validate_event` checks the header, real time,
  allowed severity, and nonempty assembled message.
- `log_analyzer/analyzer.py`: `analyze_text` combines parsing and validation
  into counts and diagnostics; `analyze_file` reads UTF-8 text from a path.
- `log_analyzer/cli.py`: `main` gets the path, reports read errors, and prints
  the analysis.
- `log_analyzer/models.py`: shared event, diagnostic, and result data types.
- `tests/` and `testdata/`: automated checks and example input files.
