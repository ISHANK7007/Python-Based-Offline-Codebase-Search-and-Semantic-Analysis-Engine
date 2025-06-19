def setup_basic_filtering_arguments(parser):
    """Set up basic filtering arguments for CLI"""
    filter_group = parser.add_argument_group('Basic Filtering')
    
    # Common field filters
    filter_group.add_argument('--name', 
                             help='Filter by name (exact match)')
    filter_group.add_argument('--path', 
                             help='Filter by file path (exact match)')
    filter_group.add_argument('--role',
                             help='Filter by semantic role')
    filter_group.add_argument('--type',
                             choices=['function', 'class', 'method', 'module'],
                             help='Filter by element type')
    filter_group.add_argument('--decorator',
                             help='Filter by decorator')
    filter_group.add_argument('--doc',
                             help='Filter by text in docstring')
                             
    # Field operation modifiers
    filter_group.add_argument('--name-startswith',
                             dest='name_startswith',
                             help='Filter by name starting with value')
    filter_group.add_argument('--name-regex',
                             dest='name_regex',
                             help='Filter by name matching regex pattern')
    filter_group.add_argument('--name-fuzzy',
                             dest='name_fuzzy',
                             help='Filter by name with fuzzy matching')
    filter_group.add_argument('--doc-includes',
                             dest='doc_includes',
                             help='Filter by docstring including text')
    
    # Logic combination
    filter_group.add_argument('--all', 
                             action='store_true',
                             help='All filters must match (AND logic, default)')
    filter_group.add_argument('--any',
                             action='store_true',
                             help='Any filter can match (OR logic)')
    filter_group.add_argument('--not',
                             action='store_true',
                             help='Negate the result (NOT logic)')
    
    # Field selection
    filter_group.add_argument('--fields',
                             help='Comma-separated list of fields to search when using --contains')
    filter_group.add_argument('--contains',
                             help='Search for text across specified fields (or all searchable fields if --fields not provided)')