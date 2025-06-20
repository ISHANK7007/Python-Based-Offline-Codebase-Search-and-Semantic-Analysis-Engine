from pathlib import Path
from cli.commands.search import SearchCommand
from tests.utils.output_normalizer import normalize_output, normalize_golden

def test_search_command_output_matches_golden(cli_output_captor, deeply_nested_repo):
    """Test that search command output matches golden files."""
    
    # Load golden file
    golden_path = Path(__file__).parent / "golden/search/basic_function_search.golden.txt"
    with open(golden_path, encoding="utf-8") as f:
        expected_output = f.read()
    
    # Run search command with test repo
    output = cli_output_captor.capture_command(
        SearchCommand,
        ["--path", str(deeply_nested_repo), "--type", "function"]
    )
    
    # Normalize both actual and expected output
    normalized_output = normalize_output(output)
    normalized_expected = normalize_golden(expected_output)
    
    # Assertion
    assert normalized_output == normalized_expected
