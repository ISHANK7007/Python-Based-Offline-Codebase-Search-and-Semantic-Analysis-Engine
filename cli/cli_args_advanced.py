def setup_advanced_filtering_arguments(parser):
    """Set up advanced filtering arguments for CLI"""
    advanced_group = parser.add_argument_group('Advanced Filtering')
    
    # Complex relationship filters
    advanced_group.add_argument('--calls',
                              help='Filter by functions that call the specified function')
    advanced_group.add_argument('--called-by',
                              help='Filter by functions called by the specified function')
    advanced_group.add_argument('--inherits',
                              help='Filter by classes that inherit from the specified class')
    advanced_group.add_argument('--imported-by',
                              help='Filter by modules that import the specified module')
    
    # Advanced matching options
    advanced_group.add_argument('--threshold',
                              type=float,
                              default=0.7,
                              help='Similarity threshold for fuzzy matching (0.0-1.0)')
    advanced_group.add_argument('--case-sensitive',
                              action='store_true',
                              help='Use case-sensitive matching')
    
    # Query expression
    advanced_group.add_argument('--query', '-q',
                              help='Advanced query expression using the query DSL')
    
    # Filter file
    advanced_group.add_argument('--filter-file',
                              help='Load complex filters from a filter definition file')