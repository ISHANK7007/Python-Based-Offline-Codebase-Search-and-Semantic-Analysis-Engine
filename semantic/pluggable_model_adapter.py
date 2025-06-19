import os
import tempfile
import subprocess
import json
import shutil
import pytest

def test_ci_pipeline_integration():
    """Test integration with a CI pipeline script for detecting breaking changes."""
    output_dir = tempfile.mkdtemp()
    json_output = os.path.join(output_dir, "diff_results.json")
    markdown_output = os.path.join(output_dir, "diff_report.md")

    # Create a mock CI script that reads JSON and exits based on breaking change
    script_path = os.path.join(output_dir, "ci_process.py")
    with open(script_path, 'w') as f:
        f.write(
            "import json\n"
            "import sys\n"
            "with open(sys.argv[1], 'r') as f:\n"
            "    results = json.load(f)\n"
            "if results.get('impact', {}).get('api_breaking', False):\n"
            "    sys.exit(1)\n"
            "else:\n"
            "    sys.exit(0)\n"
        )

    try:
        # Act - Run semantic-indexer with JSON output (breaking change case)
        subprocess.run([
            "semantic-indexer", "compare", "app.utils.process_data",
            "--src1=./tests/fixtures/return_type_change/v1",
            "--src2=./tests/fixtures/return_type_change/v2",
            "--format=json",
            f"--output-file={json_output}"
        ], check=True)

        # Generate markdown report
        subprocess.run([
            "semantic-indexer", "compare", "app.utils.process_data",
            "--src1=./tests/fixtures/return_type_change/v1",
            "--src2=./tests/fixtures/return_type_change/v2",
            "--format=markdown",
            f"--output-file={markdown_output}"
        ], check=True)

        # Run CI script on output
        result = subprocess.run(["python", script_path, json_output], capture_output=True)

        # Assert
        assert os.path.exists(json_output)
        assert os.path.exists(markdown_output)
        assert result.returncode == 1  # API breaking should trigger failure

        # Inspect JSON content
        with open(json_output, 'r') as f:
            data = json.load(f)
            assert data['impact']['api_breaking'] is True
            assert data['changes']['returns']['type_changed'] is True

    finally:
        shutil.rmtree(output_dir)
