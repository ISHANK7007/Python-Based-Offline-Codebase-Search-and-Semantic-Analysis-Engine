# cli.py
import argparse
import sys
from pathlib import Path
from cli_factory import create_cli

def main():
    parser = argparse.ArgumentParser(
        description="Semantic code analysis and querying tool"
    )
    
    # Global arguments
    parser.add_argument(
        "--codebase-dir", 
        type=Path, 
        default=Path.cwd(),
        help="Root directory of the codebase to analyze"
    )
    parser.add_argument(
        "--index-path", 
        type=Path, 
        help="Path to the pre-built index file"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug logging"
    )
    
    # Setup subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Initialize CLI environment
    services, commands = create_cli()
    
    # Configure command parsers
    for name, command in commands.items():
        command_parser = subparsers.add_parser(name, help=command.__doc__)
        command.configure_parser(command_parser)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Execute command
        return commands[args.command].run(args)
    except Exception as e:
        if args.debug:
            raise
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())