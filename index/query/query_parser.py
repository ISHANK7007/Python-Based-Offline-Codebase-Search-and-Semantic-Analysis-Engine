import shlex
from index.query.filters import AndFilter, OrFilter, NotFilter, FieldFilter
from index.query.semantic_filters import RoleFilter, DecoratorFilter
from index.query.matching_strategies import (
    ExactMatchingStrategy,
    StartsWithStrategy,
    RegexStrategy,
    FuzzyStrategy
)

class QueryParser:
    def __init__(self):
        self.strategies = {
            'exact': ExactMatchingStrategy(),
            'startswith': StartsWithStrategy(),
            'regex': RegexStrategy(),
            'fuzzy': FuzzyStrategy(),
        }

    def parse(self, query_string):
        """Parse a full query string into a filter expression tree"""
        self.tokens = shlex.split(query_string)
        self.pos = 0
        return self._parse_expression()

    def _parse_expression(self):
        node = self._parse_term()

        while self._peek() in ('AND', 'OR'):
            op = self._next()
            right = self._parse_term()
            if op == 'AND':
                node = AndFilter([node, right])
            elif op == 'OR':
                node = OrFilter([node, right])

        return node

    def _parse_term(self):
        token = self._peek()

        if token == 'NOT':
            self._next()
            operand = self._parse_term()
            return NotFilter(operand)

        if token and token.startswith('--'):
            return self._parse_filter()

        raise ValueError(f"Unexpected token in query: {token}")

    def _parse_filter(self):
        field_token = self._next()
        field = field_token[2:]  # Remove leading '--'

        # Special cases: semantic filters
        if field == 'role':
            value = self._next()
            return RoleFilter(value)

        if field == 'decorator':
            value = self._next()
            return DecoratorFilter(value)

        # General field filters (with strategy support)
        strategy_token = self._peek()
        if strategy_token in self.strategies or (strategy_token and ':' in strategy_token):
            strategy_and_value = [self._next(), self._next()]
        else:
            strategy_and_value = [self._next()]

        return self._parse_field_filter(field, strategy_and_value)

    def _parse_field_filter(self, field_name, tokens):
        """Parse a field filter with optional strategy"""
        if len(tokens) >= 2 and (tokens[0] in self.strategies or ':' in tokens[0]):
            strategy_name = tokens[0]
            value = tokens[1]

            if ':' in strategy_name:
                base_strategy, config = strategy_name.split(':', 1)
                if base_strategy == 'fuzzy':
                    try:
                        threshold = float(config)
                        strategy = FuzzyStrategy(threshold=threshold)
                    except ValueError:
                        strategy = self.strategies.get(base_strategy, ExactMatchingStrategy())
                else:
                    strategy = self.strategies.get(base_strategy, ExactMatchingStrategy())
            else:
                strategy = self.strategies[strategy_name]
        else:
            strategy = ExactMatchingStrategy()
            value = tokens[0]

        return FieldFilter(field_name, value, strategy)

    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _next(self):
        token = self._peek()
        self.pos += 1
        return token
