import os
from pathlib import Path
from typing import List, Dict, Any
from cli.commands.search import SearchCommand

class GoldenFileGenerator:
    """Utility for generating and updating golden files for CLI output."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def generate_search_golden(
        self, 
        name: str, 
        query: str, 
        filters: Dict[str, Any], 
        formats: List[str] = ["txt", "json"]
    ):
        """Generate golden files for the search command."""
        repo_path = self._create_deterministic_repo()

        for fmt in formats:
            args = ["--path", str(repo_path), "--query", query, "--format", fmt]
            for k, v in filters.items():
                args.extend([f"--{k}", str(v)])

            output = self._run_command(SearchCommand, args)
            output = self._normalize_output(output, fmt)

            file_path = self.output_dir / "search" / f"{name}.golden.{fmt}"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(output)

    def _normalize_output(self, output: str, format_: str) -> str:
        """Normalize output for deterministic golden file creation."""
        lines = output.splitlines()
        sanitized = []
        for line in lines:
            line = line.replace(str(Path.cwd()), "<PROJECT_ROOT>")
            line = line.replace("\\", "/")
            line = line.replace("202", "20X")  # Generic year masking
            sanitized.append(line)
        return "\n".join(sanitized)

    def _create_deterministic_repo(self) -> Path:
        """Simulate or link a deterministic mock repository."""
        mock_repo_path = Path("mockpackage").absolute()
        if not mock_repo_path.exists():
            raise FileNotFoundError("Expected mockpackage/ directory not found")
        return mock_repo_path

    def _run_command(self, command_cls, args: List[str]) -> str:
        """Simulate CLI command execution and return its output."""
        from io import StringIO
        import contextlib

        out = StringIO()
        with contextlib.redirect_stdout(out):
            command = command_cls()
            command.run(args)
        return out.getvalue()
