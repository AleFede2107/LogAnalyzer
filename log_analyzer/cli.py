from pathlib import Path

from .analyzer import analyze_file


def main() -> None:
    """Prompt for a path, report file errors, and print analysis results."""
    path_text = input("Enter the path to a log file: ").strip().strip('"')
    if not path_text:
        print("No file path was provided.")
        return

    try:
        result = analyze_file(Path(path_text))
    except FileNotFoundError:
        print(f"File not found: {path_text}")
        return
    except PermissionError:
        print(f"Permission denied while reading: {path_text}")
        return
    except UnicodeDecodeError:
        print(f"Could not read {path_text} as UTF-8 text.")
        return
    except OSError as error:
        print(f"Could not read {path_text}: {error}")
        return

    if result.is_empty_file:
        print("The selected file is empty.")

    print(f"Total valid events: {result.valid_event_count}")
    for severity, count in result.severity_counts.items():
        print(f"{severity}: {count}")
    print(f"Malformed events: {result.malformed_event_count}")

    if result.diagnostics:
        print("Diagnostics:")
        for diagnostic in result.diagnostics:
            print(f"  Line {diagnostic.line_number}: {diagnostic.reason}")
    else:
        print("Diagnostics: none")
