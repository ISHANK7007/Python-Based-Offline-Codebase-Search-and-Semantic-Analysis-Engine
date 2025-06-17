import argparse
import sys
from pathlib import Path

# Import command modules from local structure
from cli.commands.search import SearchCommand
from cli.commands.summarize import SummarizeCommand
# from cli.commands.describe import DescribeCommand  # Uncomment when implemented

from index.codebase_index import CodebaseIndex
from index.query.query_engine import QueryEngine

def main():
    parser = argparse.ArgumentParser(
        description="Semantic code analysis and querying tool"
    )

    # Global arguments
    parser.add_argument(
        "--codebase-dir",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the codebase to analyze (default: current directory)"
    )
    parser.add_argument(
        "--index-path",
        type=Path,
        help="Path to the pre-built index file"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    # Subcommand setup
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    subparsers.required = True  # For Python 3.7+

    # Command registration
    command_parsers = {}
    commands = {
        "search": SearchCommand,
        "summarize": SummarizeCommand,
        # "describe": DescribeCommand,  # TODO: Re-enable once describe.py is added
    }

    for name, command_class in commands.items():
        command_parser = subparsers.add_parser(name, help=command_class.__doc__)
        command_parsers[name] = (command_parser, command_class)

    # Early parse to determine command
    args, _ = parser.parse_known_args()

    try:
        # Load or build the index
        codebase_index = (
            CodebaseIndex.load(args.index_path)
            if args.index_path and args.index_path.exists()
            else CodebaseIndex(args.codebase_dir).build()
        )
        query_engine = QueryEngine(codebase_index)

        # Configure selected command
        command_parser, command_class = command_parsers[args.command]
        command = command_class(codebase_index=codebase_index, query_engine=query_engine)
        command.configure_parser(command_parser)

        # Final parse after parser is configured
        args = parser.parse_args()

        # Run the selected command
        return command.run(args)

    except Exception as e:
        if getattr(args, 'debug', False):
            raise
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
