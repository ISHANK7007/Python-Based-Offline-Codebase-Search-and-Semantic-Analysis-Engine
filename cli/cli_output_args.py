# Output_code/cli/cli_output_args.py

import argparse

def setup_cli_arguments(parser):
    """Set up CLI arguments for output formatting and filtering"""

    # Output Formatting Options
    output_group = parser.add_argument_group('Output Formatting')
    output_group.add_argument(
        '--output', '-o',
        choices=['text', 'json', 'csv', 'table'],
        default='text',
        help='Output format'
    )
    output_group.add_argument(
        '--columns',
        nargs='+',
        help='Columns to display in output'
    )
    output_group.add_argument(
        '--sort-by',
        help='Field to sort results by'
    )
    output_group.add_argument(
        '--max-width',
        type=int,
        help='Maximum width for text fields'
    )

    # Filter Options
    parser.add_argument('--name')
    parser.add_argument('--name-startswith')
    parser.add_argument('--name-regex')
    parser.add_argument('--name-fuzzy')
    parser.add_argument('--doc')
    parser.add_argument('--doc-includes')
    parser.add_argument('--role')
    parser.add_argument('--type')
    parser.add_argument('--path')
    parser.add_argument('--decorator')
    parser.add_argument('--contains')
    parser.add_argument('--fields')
    parser.add_argument('--calls')
    parser.add_argument('--called-by')
    parser.add_argument('--inherits')
    parser.add_argument('--imported-by')
    parser.add_argument('--threshold', type=float, default=0.7)
    parser.add_argument('--any', action='store_true')
    parser.add_argument('--not', action='store_true')


def process_formatting_args(args, query_engine):
    """Process formatting arguments from CLI"""
    format_config = {}

    if args.output:
        format_config['format'] = args.output

    if args.columns:
        format_config['columns'] = args.columns

    if args.sort_by:
        format_config['sort_by'] = args.sort_by

    if args.max_width:
        format_config['max_width'] = {
            'name': args.max_width,
            'file_path': args.max_width,
            'doc': args.max_width,
        }

    if format_config:
        query_engine.configure_output(**format_config)


def parse_output_args(arg_list):
    """Simulate CLI arg parsing from a list"""
    parser = argparse.ArgumentParser(description="Offline Codebase Search CLI")
    setup_cli_arguments(parser)
    args = parser.parse_args(arg_list)
    return args
