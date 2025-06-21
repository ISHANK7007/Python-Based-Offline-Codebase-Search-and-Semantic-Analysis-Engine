import argparse
from shutil import get_terminal_size

def extend_compare_parser(parser: argparse.ArgumentParser):
    parser.add_argument('symbol', help='Symbol name to compare (e.g., module.Class.method)')
    parser.add_argument('--src1', required=True, help='First source directory')
    parser.add_argument('--src2', required=True, help='Second source directory')
    parser.add_argument('--attributes', nargs='+',
                        choices=['decorators', 'arguments', 'returns', 'docstring', 'callers', 'callees'],
                        default=['decorators', 'arguments', 'returns', 'docstring'],
                        help='Specific semantic attributes to compare')
    parser.add_argument('--format', choices=['text', 'json', 'yaml', 'markdown'],
                        default='text', help='Output format style')
    parser.add_argument('--output-file', help='Write diff output to file')
    parser.add_argument('--strict', action='store_true', help='Exit with non-zero code if breaking change found')

    # Fuzzy matching for renamed symbol detection
    parser.add_argument('--fuzzy-match', action='store_true',
                        help='Attempt to find renamed symbols using fuzzy matching')
    parser.add_argument('--match-threshold', type=float, default=0.7,
                        help='Similarity threshold for fuzzy matching (0.0-1.0)')

    # Display options
    diff_group = parser.add_argument_group('Diff display options')
    diff_group.add_argument('--diff', choices=['unified', 'side-by-side', 'none'],
                            default='unified', help='Display diff format')
    diff_group.add_argument('--width', type=int, default=get_terminal_size((80, 20)).columns,
                            help='Terminal width (only applies to side-by-side diffs)')
    diff_group.add_argument('--syntax-highlight', action='store_true', default=True,
                            help='Highlight syntax in output blocks')
    diff_group.add_argument('--line-numbers', action='store_true', default=True,
                            help='Show line numbers in formatted output')

    return parser