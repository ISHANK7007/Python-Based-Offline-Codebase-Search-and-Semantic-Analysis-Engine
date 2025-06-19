import os
import pytest

from semantic.diff_output_formatter import TextDiffFormatter
from cli.commands.compare_executor import VersionManager  # Adjust if VersionManager is elsewhere

# Test config constants (adjust as needed)
FIXTURES_DIR = "tests/fixtures"
GOLDEN_FILES_DIR = "tests/golden"
UPDATE_GOLDEN_FILES = False

@pytest.mark.parametrize("scenario", [
    "identical",
    "decorator_change",
    "argument_change",
    "return_type_change",
    "body_change",
    "deleted",
    "added",
    "renamed"
])
def test_text_formatter_output(scenario):
    """Test text formatter output for different scenarios."""
    # Arrange
    version_manager = VersionManager()
    fixture_dir = os.path.join(FIXTURES_DIR, scenario)

    diff = version_manager.compare_symbols(
        "app.utils.process_data",
        os.path.join(fixture_dir, "v1"),
        os.path.join(fixture_dir, "v2"),
        fuzzy_match=(scenario == "renamed")
    )

    formatter = TextDiffFormatter(color_enabled=False)

    # Act
    output = formatter.format_diff(diff)

    # Assert
    golden_file = os.path.join(GOLDEN_FILES_DIR, f"text_{scenario}.txt")

    if UPDATE_GOLDEN_FILES:
        with open(golden_file, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        assert os.path.exists(golden_file), f"Missing golden file: {golden_file}"
        with open(golden_file, 'r', encoding='utf-8') as f:
            expected = f.read()
        assert output == expected, f"Text formatter output mismatch for scenario '{scenario}'"
