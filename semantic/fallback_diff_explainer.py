import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import os
import pytest
from cli.commands.version_manager import VersionManager


from index.formatter.markdown_formatter import MarkdownDiffFormatter

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
GOLDEN_FILES_DIR = os.path.join(os.path.dirname(__file__), "golden")
UPDATE_GOLDEN_FILES = False

@pytest.mark.parametrize("scenario", [
    "identical",
    "decorator_change",
    "argument_change",
    "return_type_change",
    "deleted",
    "body_change",
    "complex_change"
])
def test_markdown_formatter_output(scenario):
    """Test markdown formatter output for different scenarios."""
    fixture_dir = os.path.join(FIXTURES_DIR, scenario)
    version_manager = VersionManager()

    diff = version_manager.compare_symbols(
        "app.utils.process_data",
        os.path.join(fixture_dir, "v1"),
        os.path.join(fixture_dir, "v2")
    )

    formatter = MarkdownDiffFormatter()
    output = formatter.format_diff(diff)

    golden_file = os.path.join(GOLDEN_FILES_DIR, f"markdown_{scenario}.md")

    if UPDATE_GOLDEN_FILES:
        with open(golden_file, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        with open(golden_file, 'r', encoding='utf-8') as f:
            expected_output = f.read()
        assert output == expected_output, f"Mismatch in scenario: {scenario}"

    try:
        import commonmark
        parser = commonmark.Parser()
        parser.parse(output)
    except ImportError:
        pytest.skip("commonmark not installed – skipping markdown parse validation")
    except Exception as e:
        pytest.fail(f"Markdown parse failed: {e}")
