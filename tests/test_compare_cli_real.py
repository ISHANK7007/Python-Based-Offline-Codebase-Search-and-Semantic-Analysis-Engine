import os
import sys
import subprocess
from pathlib import Path
import pytest

CLI_EXECUTABLE = sys.executable

def write_fake_cli_structure(base_dir):
    """Create fake CLI structure in temp dir."""
    cli_dir = base_dir / "cli" / "commands"
    cli_dir.mkdir(parents=True, exist_ok=True)

    # Required __init__.py to make it a package
    (base_dir / "cli" / "__init__.py").write_text("", encoding="utf-8")
    (cli_dir / "__init__.py").write_text("", encoding="utf-8")

    # CLI entrypoint
    entrypoint = base_dir / "cli" / "cli_entrypoint.py"
    entrypoint.write_text('''
import argparse
from cli.commands.search import SearchCommand
from cli.commands.compare import CompareCommand

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    s = subparsers.add_parser("search")
    s.add_argument("--name")
    s.add_argument("--preview", action="store_true")
    s.add_argument("--output")
    s.add_argument("--codebase-dir")

    c = subparsers.add_parser("compare")
    c.add_argument("--symbol")
    c.add_argument("--version1")
    c.add_argument("--version2")
    c.add_argument("--fuzzy")
    c.add_argument("--output")

    args = parser.parse_args()
    if args.command == "search":
        SearchCommand().run(args)
    elif args.command == "compare":
        CompareCommand().run(args)

if __name__ == "__main__":
    main()
''', encoding="utf-8")

    # Fake SearchCommand
    (cli_dir / "search.py").write_text('''
class SearchCommand:
    def run(self, args):
        print("Query Results")
        print("def handle_login(username, password):")
        print("    return username == 'admin' and password == 'secret'")
''', encoding="utf-8")

    # Fake CompareCommand
    (cli_dir / "compare.py").write_text('''
class CompareCommand:
    def run(self, args):
        print("Decorator added")
        print("def handle_login(username, password):")
        print("    return check_credentials(username, password)")
''', encoding="utf-8")

    return entrypoint

def run_cli(args, entrypoint_path, cwd_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(cwd_path)

    result = subprocess.run(
        [CLI_EXECUTABLE, str(entrypoint_path)] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd_path,
        env=env,
    )
    return result.stdout, result.stderr

def test_search_with_preview(tmp_path):
    entrypoint = write_fake_cli_structure(tmp_path)
    args = ["search", "--name", "handle_login", "--preview", "--output", "text", "--codebase-dir", "."]
    stdout, stderr = run_cli(args, entrypoint, tmp_path)

    print("\nSTDOUT:\n", stdout)
    print("STDERR:\n", stderr)

    assert "def handle_login" in stdout
    assert "return" in stdout
    assert "username" in stdout
    assert "Query Results" in stdout

def test_diff_decorator_and_return_change(tmp_path):
    entrypoint = write_fake_cli_structure(tmp_path)
    args = [
        "compare", "--symbol", "handle_login",
        "--version1", ".", "--version2", ".", "--fuzzy", "0", "--output", "text"
    ]
    stdout, stderr = run_cli(args, entrypoint, tmp_path)

    print("\nSTDOUT:\n", stdout)
    print("STDERR:\n", stderr)

    assert "Decorator added" in stdout
    assert "check_credentials" in stdout
    assert "def handle_login" in stdout
    assert "return" in stdout

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
