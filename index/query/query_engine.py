from index.query.query_plan_optimizer import QueryPlanOptimizer
from index.query.filters import AndFilter
from index.query.field_filter import FieldFilter
from index.query.semantic_filters import RoleFilter, DecoratorFilter
from index.query.matching_strategies import (
    FuzzyStrategy,
    RegexStrategy,
    ExactMatchingStrategy
)

class QueryEngine:
    def __init__(self, codebase_index):
        self.index = codebase_index
        self.optimizer = QueryPlanOptimizer(codebase_index)
        self.expensive_strategies = [FuzzyStrategy, RegexStrategy]
        self.formatter = None  # Added for output formatting

    def set_formatter(self, formatter):
        """Assign an output formatter that supports `.format()`"""
        self.formatter = formatter

    def configure_output(self, **kwargs):
        """Pass formatting configuration to the formatter if supported"""
        if self.formatter and hasattr(self.formatter, "configure"):
            self.formatter.configure(**kwargs)

    def query(self, filter_expression, output_format='text'):
        """Execute query with optimization and format results"""
        if filter_expression is None:
            results = list(self.index.all_elements())
        elif self._is_simple_indexed_lookup(filter_expression):
            results = self._direct_lookup(filter_expression)
        elif self._can_use_index_directly(filter_expression):
            results = self._query_with_index(filter_expression)
        elif isinstance(filter_expression, AndFilter) and self._contains_expensive_strategy(filter_expression):
            results = self._optimized_execution(filter_expression)
        else:
            plan = self.optimizer.create_execution_plan(filter_expression)
            results = plan.execute(self.index)

        if self.formatter:
            return self.formatter.format(results, output_format)
        return results

    def build_filter_from_query_string(self, query_string):
        """Convert string queries into filter objects using QueryParser"""
        from index.query.query_parser import QueryParser
        return QueryParser().parse(query_string)

    def _contains_expensive_strategy(self, filter_expr):
        if hasattr(filter_expr, 'strategy'):
            return isinstance(filter_expr.strategy, tuple(self.expensive_strategies))
        if hasattr(filter_expr, 'filters'):
            return any(self._contains_expensive_strategy(f) for f in filter_expr.filters)
        return False

    def _optimized_execution(self, and_filter):
        """Run cheap filters first, then expensive ones on narrowed results"""
        cheap_filters = []
        expensive_filters = []

        for f in and_filter.filters:
            (expensive_filters if self._contains_expensive_strategy(f) else cheap_filters).append(f)

        candidates = self.index.all_elements()
        if cheap_filters:
            cheap_and = AndFilter(cheap_filters)
            candidates = [item for item in candidates if cheap_and.matches(item)]

        for exp_filter in expensive_filters:
            candidates = [item for item in candidates if exp_filter.matches(item)]

        return candidates

    def _is_simple_indexed_lookup(self, filter_expr):
        """Fast-path for simple indexed field lookups"""
        return (
            isinstance(filter_expr, FieldFilter) and
            filter_expr.field_name in ('role', 'decorator', 'type') and
            isinstance(filter_expr.strategy, ExactMatchingStrategy)
        )

    def _direct_lookup(self, filter_expr):
        """Use direct index map for fast response"""
        field = filter_expr.field_name
        value = filter_expr.value
        return {
            'role': self.index.role_index.get(value, []),
            'decorator': self.index.decorator_index.get(value, []),
            'type': self.index.type_index.get(value, [])
        }.get(field, [])

    def _can_use_index_directly(self, filter_expr):
        """Detect semantic filters with direct indexing support"""
        return isinstance(filter_expr, (RoleFilter, DecoratorFilter))

    def _query_with_index(self, filter_expr):
        """Run direct index query for semantic filters"""
        if isinstance(filter_expr, RoleFilter):
            return self.index.role_index.get(filter_expr.role_name, [])
        if isinstance(filter_expr, DecoratorFilter):
            return self.index.decorator_index.get(filter_expr.decorator_name, [])
        return []
