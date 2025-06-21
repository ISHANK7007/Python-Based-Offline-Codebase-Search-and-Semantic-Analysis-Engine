import argparse
import sys
import traceback
from cli.commands.base import Command
from cli.commands.compare_args import extend_compare_parser
from cli.commands.compare_executor import run_comparison
from cli.commands.compare_output import get_diff_formatter
from index.query.symbol_matcher import SymbolMatcher
from models.semantic_diff_model import SemanticFunctionDiff
from semantic.semantic_diff_engine import VersionManager


class CompareCommand(Command):
    """Compare semantic differences between two versions of code elements"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version_manager = kwargs.get('version_manager') or VersionManager()

    def configure_parser(self, parser):
        parser.add_argument('symbol', help='Symbol name to compare (e.g., module.Class.method)')
        parser.add_argument('--src1', required=True, help='First source directory')
        parser.add_argument('--src2', required=True, help='Second source directory')
        parser.add_argument('--attributes', nargs='+',
                            choices=['decorators', 'arguments', 'returns', 'docstring', 'callers', 'callees'],
                            default=['decorators', 'arguments', 'returns', 'docstring'],
                            help='Specific attributes to compare')
        parser.add_argument('--format', choices=['text', 'json', 'yaml', 'markdown'],
                            default='text', help='Output format')
        parser.add_argument('--output-file', help='Path to write formatted diff output')
        parser.add_argument('--strict', action='store_true', help='Fail with exit code if breaking changes are found')

        # Fuzzy match options
        parser.add_argument('--fuzzy-match', action='store_true', help='Attempt to find renamed symbols')
        parser.add_argument('--match-threshold', type=float, default=0.7,
                            help='Similarity threshold for fuzzy matching (0.0-1.0)')

        # Diff output options
        diff_group = parser.add_argument_group('Diff display options')
        diff_group.add_argument('--diff', choices=['unified', 'side-by-side', 'none'],
                                default='unified', help='Diff display style')
        diff_group.add_argument('--width', type=int, default=None,
                                help='Terminal width for side-by-side diffs')
        diff_group.add_argument('--syntax-highlight', action='store_true', default=True,
                                help='Enable syntax highlighting for code blocks')
        diff_group.add_argument('--line-numbers', action='store_true', default=True,
                                help='Show line numbers in code blocks')

    def run(self, args):
        diff = self.version_manager.compare_symbols(
            args.symbol,
            args.src1,
            args.src2,
            attributes=args.attributes,
            fuzzy_match=args.fuzzy_match,
            threshold=args.match_threshold
        )

        if not diff:
            print(f"Symbol '{args.symbol}' not found in one or both codebases")
            return 1

        formatter = get_diff_formatter(args.format,
                                       display_mode=args.diff,
                                       color_enabled=not getattr(args, 'no_color', False),
                                       syntax_highlight=args.syntax_highlight,
                                       line_numbers=args.line_numbers,
                                       width=args.width)

        output = formatter.format_diff(diff)

        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(output)
        else:
            print(output)

        # Exit codes for CI/CD pipelines
        if diff.availability == SemanticFunctionDiff.AVAILABILITY_REMOVED:
            return 2 if args.strict else 0
        elif diff.impact.get('api_breaking', False):
            return 1 if args.strict else 0
        return 0


def main():
    parser = argparse.ArgumentParser(description="Semantic code analyzer and diff tool")
    subparser = parser.add_subparsers(dest="command", required=True)
    compare_parser = subparser.add_parser("compare", help="Compare semantic differences between versions")
    cmd = CompareCommand()
    cmd.configure_parser(compare_parser)

    args = parser.parse_args()
    try:
        exit_code = cmd.run(args)
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if hasattr(args, 'debug') and args.debug:
            traceback.print_exc()
        sys.exit(3)