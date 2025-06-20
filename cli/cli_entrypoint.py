import argparse
import sys
from pathlib import Path

# ✅ Patch sys.path for local imports (supports both direct and subprocess/pytest execution)
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ✅ Local imports from within project
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
    subparsers.required = True  # Python ≥ 3.7

    # Register commands dynamically
    command_parsers = {}
    commands = {
        "search": SearchCommand,
        "summarize": SummarizeCommand,
        # "describe": DescribeCommand,  # Uncomment once implemented
    }

    for name, command_class in commands.items():
        subparser = subparsers.add_parser(name, help=command_class.__doc__)
        command_parsers[name] = (subparser, command_class)

    # Early parse just to get the selected command
    args, _ = parser.parse_known_args()

    try:
        # Load or build the index
        codebase_index = (
            CodebaseIndex.load(args.index_path)
            if args.index_path and args.index_path.exists()
            else CodebaseIndex(args.codebase_dir).build()
        )
        query_engine = QueryEngine(codebase_index)

        # Retrieve command-specific parser + command class
        command_parser, command_class = command_parsers[args.command]
        command = command_class(codebase_index=codebase_index, query_engine=query_engine)
        command.configure_parser(command_parser)

        # Now fully parse arguments and execute
        args = parser.parse_args()
        return command.run(args)

    except Exception as e:
        if getattr(args, 'debug', False):
            raise
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
