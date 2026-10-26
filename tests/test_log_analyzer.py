import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from log_analyzer.analyzer import analyze_file, analyze_text
from log_analyzer.cli import main

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class AnalyzeFileTests(unittest.TestCase):
    def test_valid_fixture(self) -> None:
        result = analyze_file(PROJECT_ROOT / "testdata" / "valid.log")

        self.assertEqual(result.valid_event_count, 3)
        self.assertEqual(result.severity_counts, {"INFO": 1, "WARNING": 1, "ERROR": 1})
        self.assertEqual(result.malformed_event_count, 0)
        self.assertEqual(result.diagnostics, [])

    def test_mixed_fixture(self) -> None:
        result = analyze_file(PROJECT_ROOT / "testdata" / "mixed.log")

        self.assertEqual(result.valid_event_count, 1)
        self.assertEqual(result.severity_counts, {"INFO": 1, "WARNING": 0, "ERROR": 0})
        self.assertEqual(result.malformed_event_count, 3)
        self.assertEqual(
            [(diagnostic.line_number, diagnostic.reason) for diagnostic in result.diagnostics],
            [
                (1, "invalid calendar date '32/10/26'"),
                (2, "text appears before the first event"),
                (6, "time '25:61' is not a real 24-hour time"),
                (
                    7,
                    "severity 'info' is invalid; use INFO, WARNING, or ERROR",
                ),
                (8, "message is empty or contains only whitespace"),
            ],
        )

    def test_empty_text_is_identified(self) -> None:
        result = analyze_text("")

        self.assertTrue(result.is_empty_file)
        self.assertEqual(result.valid_event_count, 0)
        self.assertEqual(result.malformed_event_count, 0)

    def test_leading_blank_is_diagnosed_but_not_counted_as_event(self) -> None:
        result = analyze_text("\n25/10/26 14:30 [INFO] Ready")

        self.assertEqual(result.valid_event_count, 1)
        self.assertEqual(result.malformed_event_count, 0)
        self.assertEqual(result.diagnostics[0].line_number, 1)
        self.assertEqual(result.diagnostics[0].reason, "blank line has no preceding event")

    def test_two_digit_years_map_to_2000_through_2099(self) -> None:
        result = analyze_text(
            "01/01/00 00:00 [INFO] First year\n"
            "31/12/99 23:59 [ERROR] Last year"
        )

        self.assertEqual(result.valid_event_count, 2)
        self.assertEqual(result.severity_counts, {"INFO": 1, "WARNING": 0, "ERROR": 1})
        self.assertEqual(result.malformed_event_count, 0)

    def test_impossible_date_is_diagnosed_without_starting_an_event(self) -> None:
        result = analyze_text(
            "25/10/26 14:30 [INFO] Ready\n"
            "32/10/26 14:31 [ERROR] This is not a new event"
        )

        self.assertEqual(result.valid_event_count, 1)
        self.assertEqual(result.malformed_event_count, 0)
        self.assertEqual(
            result.diagnostics[0].reason, "invalid calendar date '32/10/26'"
        )
        self.assertEqual(result.diagnostics[0].line_number, 2)

    def test_wrong_date_format_is_diagnosed_without_starting_an_event(self) -> None:
        result = analyze_text(
            "25/10/26 14:30 [INFO] Ready\n"
            "2026-10-25 14:31 [ERROR] Not in the required format"
        )

        self.assertEqual(result.valid_event_count, 1)
        self.assertEqual(result.malformed_event_count, 0)
        self.assertEqual(
            result.diagnostics[0].reason,
            "date '2026-10-25' must use DD/MM/YY",
        )
        self.assertEqual(result.diagnostics[0].line_number, 2)

    def test_seconds_are_not_accepted_for_hh_mm_format(self) -> None:
        result = analyze_text("25/10/26 14:30:00 [INFO] Not valid")

        self.assertEqual(result.valid_event_count, 0)
        self.assertEqual(result.malformed_event_count, 1)
        self.assertIn("must use HH:MM", result.diagnostics[0].reason)


class ConsoleTests(unittest.TestCase):
    def test_empty_file_has_an_understandable_message(self) -> None:
        with TemporaryDirectory() as directory:
            empty_file = Path(directory) / "empty.log"
            empty_file.write_text("", encoding="utf-8")
            output = StringIO()
            with patch("builtins.input", return_value=str(empty_file)):
                with redirect_stdout(output):
                    main()

        self.assertIn("The selected file is empty.", output.getvalue())
        self.assertIn("Total valid events: 0", output.getvalue())

    def test_missing_file_has_an_understandable_message(self) -> None:
        with TemporaryDirectory() as directory:
            missing_file = Path(directory) / "missing.log"
            output = StringIO()
            with patch("builtins.input", return_value=str(missing_file)):
                with redirect_stdout(output):
                    main()

        self.assertIn("File not found:", output.getvalue())

    def test_permission_error_has_an_understandable_message(self) -> None:
        output = StringIO()
        with patch("builtins.input", return_value="restricted.log"):
            with patch("log_analyzer.cli.analyze_file", side_effect=PermissionError):
                with redirect_stdout(output):
                    main()

        self.assertIn("Permission denied while reading:", output.getvalue())

    def test_non_utf8_file_has_an_understandable_message(self) -> None:
        with TemporaryDirectory() as directory:
            invalid_file = Path(directory) / "invalid.log"
            invalid_file.write_bytes(b"\xff")
            output = StringIO()
            with patch("builtins.input", return_value=str(invalid_file)):
                with redirect_stdout(output):
                    main()

        self.assertIn("as UTF-8 text.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
