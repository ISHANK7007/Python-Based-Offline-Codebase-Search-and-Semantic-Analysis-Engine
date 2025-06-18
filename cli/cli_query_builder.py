from index.query.query_parser import QueryParser
from index.query.filters import AndFilter, OrFilter, NotFilter
from index.query.field_filter import FieldFilter

def build_query_from_args(args):
    """Convert parsed CLI args into a filter expression"""
    parser = QueryParser()
    filters = []
    operators = []

    i = 0
    while i < len(args):
        token = args[i]

        if token.startswith('--name') or token.startswith('--doc'):
            field = token[2:]
            strategy_and_value = []

            # Collect possible strategy + value
            if i + 2 <= len(args):
                next_token = args[i + 1]
                if not next_token.startswith('--') and i + 2 < len(args):
                    strategy_and_value = [args[i + 1], args[i + 2]]
                    i += 2
                else:
                    strategy_and_value = [args[i + 1]]
                    i += 1

            filters.append(parser._parse_field_filter(field, strategy_and_value))

        elif token == '--role':
            role = args[i + 1]
            filters.append(parser._parse_filter('--role', role))
            i += 1

        elif token == '--decorator':
            decorator = args[i + 1]
            filters.append(parser._parse_filter('--decorator', decorator))
            i += 1

        elif token == 'AND':
            operators.append('AND')
        elif token == 'OR':
            operators.append('OR')
        elif token == 'NOT':
            operators.append('NOT')

        i += 1

    # Build composite filter expression
    if not filters:
        return None
    elif len(filters) == 1:
        return filters[0]
    else:
        # Currently supports only AND composition for simplicity
        return AndFilter(filters)
