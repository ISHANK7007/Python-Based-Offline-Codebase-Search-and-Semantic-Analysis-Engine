import pytest
from pathlib import Path
from cli.cli_entrypoint import main as cli_main
from io import StringIO
import contextlib

class ErrorSnapshotValidator:
    def __init__(self, base_path: Path):
        self.base_path = base_path

    def assert_error_output(self, test_case: str, args: list, expected_fragment: str):
        captured_output = self._run_cli(args)
        snapshot_path = self.base_path / f"{test_case}.error.txt"
        if "--update-snapshots" in args or not snapshot_path.exists():
            snapshot_path.write_text(captured_output)
        else:
            expected_output = snapshot_path.read_text()
            if expected_fragment not in captured_output:
                raise AssertionError(
                    f"Expected fragment not found in CLI output.Expected: {expected_fragment}Got: {captured_output}"
                )
            if captured_output != expected_output:
                raise AssertionError(
                    f"Output mismatch. Run with --update-snapshots to refresh.Diff:"
                    + self._diff(expected_output, captured_output)
                )

    def _run_cli(self, args):
        stream = StringIO()
        with contextlib.redirect_stdout(stream):
            try:
                cli_main(args)
            except SystemExit:
                pass  # CLI may call sys.exit(), which is expected
        return stream.getvalue()

    def _diff(self, expected, actual):
        import difflib
        return "\n".join(
            difflib.unified_diff(
                expected.splitlines(),
                actual.splitlines(),
                fromfile="expected",
                tofile="actual",
                lineterm=""
            )
        )

@pytest.fixture
def error_validator(tmp_path):
    return ErrorSnapshotValidator(tmp_path / "cli_errors")

def test_missing_required_argument(error_validator):
    args = ["search"]
    error_validator.assert_error_output(
        "missing_required_argument",
        args,
        "error: the following arguments are required"
    )

def test_invalid_filter_argument(error_validator):
    args = ["search", "--query", "auth*", "--filter", "invalid::filter"]
    error_validator.assert_error_output(
        "invalid_filter_argument",
        args,
        "Invalid filter syntax"
    )

def test_unknown_command(error_validator):
    args = ["unknown_command"]
    error_validator.assert_error_output(
        "unknown_command",
        args,
        "Unknown command"
    )