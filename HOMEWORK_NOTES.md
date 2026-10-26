# Homework Notes: AI as a Tool for Developers

This file records what happened during development. It is not a substitute for
your own personal reflection; keep only statements that match your experience.

## AI support used

- Helped organize the program into parsing, validation, file analysis, console
  output, shared data models, and tests.
- Drafted the Python implementation and sample log files.
- Proposed test expectations before running the code, then compared those
  expectations against actual unit-test and console output.
- Added error handling and checks for missing paths, permission errors, empty
  files, and non-UTF-8 input.

## Decisions made by the student

- Use `HH:MM`, not hour-only time or seconds.
- Attach a blank line as `all clear` in the preceding event. Diagnose a blank
  line that has no preceding event.
- Start an event only at a line beginning with a calendar-valid `DD/MM/YY`
  date. A valid date starts a new event even if its time or severity is
  malformed.
- Diagnose impossible or differently formatted dates as line-level input
  problems. They do not start events; if an event is open, the line continues
  that message.
- Count invalid events, not physical lines. Preamble and unattached blank/date
  diagnostics are not events and do not increase this count.
- Map all two-digit years to 2000–2099.
- Accept whitespace separators, trim message-edge whitespace, and require a
  non-whitespace message.
- Count `ERROR` as an application severity when its event is valid.

## A real suggestion that was refined

During clarification, the AI initially suggested treating a date-shaped date
plus a time-shaped field as an event boundary, even if the date was impossible.
The student selected a narrower rule: only a calendar-valid date starts an
event. When the impossible-date consequence became relevant, the student
clarified that such a line should receive an invalid-date diagnostic and
continue the prior message (or be diagnosed as preamble if there is no prior
event). The parser and tests follow that choice. This was an improvable initial
suggestion, not a claim that a test exposed a bug.

## Verified test results

The expected and observed outputs for both sample files are documented in
[TEST_EVIDENCE.md](./TEST_EVIDENCE.md). The final recorded run used Python
3.11.9; all 12 unit tests passed, and both console outputs matched the
pre-calculated results.

## Personal reflection: complete in your own words

Use this as a starting point for a 1–3 page reflection. Replace the prompts
with your own experience; do not claim a lesson or feeling that is not yours.

1. **Where AI helped:** Which generated structure, explanation, test, or
   debugging step actually saved you effort? What did you still need to check?
2. **Your decisions:** Which validation rules did you choose, and why did
   those choices matter for the output?
3. **Checking the suggestion:** Explain the boundary-rule suggestion above.
   What did you notice was incomplete, how did you clarify it, and how did the
   resulting behavior appear in the code or test evidence?
4. **What you learned:** What will you do differently when using AI on another
   programming task? Include a specific example from this project and explain
   how you would verify an AI-generated answer next time.
