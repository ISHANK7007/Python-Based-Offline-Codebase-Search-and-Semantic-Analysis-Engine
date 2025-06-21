import os
import tempfile
import pytest

from cli.commands.version_manager import VersionManager  # Corrected import based on your folder structure


@pytest.fixture
def version_manager():
    """Create a VersionManager with test configuration."""
    return VersionManager(cache_dir=os.path.join(tempfile.gettempdir(), "test_semantic_indexer_cache"))


def assert_terminal_output_matches(actual, expected):
    """Compare terminal outputs allowing for minor differences."""
    actual_lines = [line.rstrip() for line in actual.splitlines()]
    expected_lines = [line.rstrip() for line in expected.splitlines()]
    
    assert len(actual_lines) == len(expected_lines), "Line count differs"

    for i, (a_line, e_line) in enumerate(zip(actual_lines, expected_lines)):
        assert a_line == e_line, f"Line {i+1} differs: \n  Actual: {a_line}\nExpected: {e_line}"


# Test configuration constants
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
GOLDEN_FILES_DIR = os.path.join(os.path.dirname(__file__), "golden_files")
UPDATE_GOLDEN_FILES = os.environ.get("UPDATE_GOLDEN_FILES", "0") == "1"
