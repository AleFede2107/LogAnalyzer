# Test Evidence

## Test method

Tests were run with Python 3.11.9 on the standard library only:

```text
python -m unittest discover -s tests -v
```

Result: **12 tests passed**. The test suite includes file analysis, date and
time validation, multiline and blank-line handling, and console messages for
empty, missing, permission-denied, and non-UTF-8 files.

The two example files were also selected through the console program using
`python -m log_analyzer`.

## `testdata/valid.log`

Input includes three valid events, an INFO message split across lines, a blank
line inside that message, and continuations for INFO and ERROR. The blank line
is interpreted as the message line `all clear`.

Expected:

- Total valid events: 3
- INFO: 1
- WARNING: 1
- ERROR: 1
- Malformed events: 0
- Diagnostics: none

Actual console output:

```text
Total valid events: 3
INFO: 1
WARNING: 1
ERROR: 1
Malformed events: 0
Diagnostics: none
```

Result: **matches expected**.

## `testdata/mixed.log`

Input includes an impossible calendar date, text before the first valid event,
a valid multiline INFO event with an internal blank line, an invalid time, a
lowercase severity, and an event with an empty message.

Expected:

- Total valid events: 1
- INFO: 1
- WARNING: 0
- ERROR: 0
- Malformed events: 3
- Diagnostics:
  - Line 1: impossible calendar date (not counted as an event)
  - Line 2: preamble before the first event
  - Line 6: invalid 24-hour time
  - Line 7: invalid severity casing
  - Line 8: empty message

Actual console output:

```text
Total valid events: 1
INFO: 1
WARNING: 0
ERROR: 0
Malformed events: 3
Diagnostics:
  Line 1: invalid calendar date '32/10/26'
  Line 2: text appears before the first event
  Line 6: time '25:61' is not a real 24-hour time
  Line 7: severity 'info' is invalid; use INFO, WARNING, or ERROR
  Line 8: message is empty or contains only whitespace
```

Result: **matches expected**.

## Additional validation

Automated tests also verified that `YY=00` maps to 2000, `YY=99` maps to 2099,
seconds are rejected under the selected HH:MM rule, an invalid date does not
start a new event, and leading blank lines are diagnosed without increasing
the malformed-event count.
