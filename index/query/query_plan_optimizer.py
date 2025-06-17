from index.query.field_filter import FieldFilter
from index.query.filters import AndFilter, OrFilter

from index.query.matching_strategies import (
    ExactMatchingStrategy,
    StartsWithStrategy,
    RegexStrategy,
    FuzzyStrategy
)
from index.query.execution_plan import ExecutionPlan

class QueryPlanOptimizer:
    """Analyzes filter expression and creates an optimized execution plan"""
    
    def __init__(self, index):
        self.index = index

        # Only use fields that actually exist in CodebaseIndex
        self.indexable_fields = {
            'decorator': getattr(self.index, 'decorator_index', {}),
            'doc': getattr(self.index, 'doc_index', {}),
        }

        self.prefix_indexable = {
            'name': getattr(self.index, 'name_prefix_index', {}),
            'file_path': getattr(self.index, 'path_prefix_index', {}),
        }

    def create_execution_plan(self, filter_expression):
        indexed_lookups = self._extract_indexed_lookups(filter_expression)
        prefix_lookups = self._extract_prefix_lookups(filter_expression)
        remaining_filters = self._extract_remaining_filters(
            filter_expression, indexed_lookups + prefix_lookups
        )
        sorted_remaining = self._sort_by_estimated_cost(remaining_filters)
        return ExecutionPlan(
            indexed_lookups=indexed_lookups,
            prefix_lookups=prefix_lookups,
            remaining_filters=sorted_remaining
        )

    def _extract_indexed_lookups(self, filter_expr):
        if isinstance(filter_expr, FieldFilter):
            field = filter_expr.field_name
            if field in self.indexable_fields and isinstance(filter_expr.strategy, ExactMatchingStrategy):
                return [filter_expr]
        if isinstance(filter_expr, (AndFilter, OrFilter)) and hasattr(filter_expr, 'filters'):
            result = []
            for child in filter_expr.filters:
                result.extend(self._extract_indexed_lookups(child))
            return result
        return []

    def _extract_prefix_lookups(self, filter_expr):
        if isinstance(filter_expr, FieldFilter):
            field = filter_expr.field_name
            if field in self.prefix_indexable and isinstance(filter_expr.strategy, StartsWithStrategy):
                return [filter_expr]
        if isinstance(filter_expr, (AndFilter, OrFilter)) and hasattr(filter_expr, 'filters'):
            result = []
            for child in filter_expr.filters:
                result.extend(self._extract_prefix_lookups(child))
            return result
        return []

    def _extract_remaining_filters(self, filter_expr, already_optimized):
        """Extract filters not already covered by index or prefix lookups"""
        optimized_set = set(already_optimized)
        results = []

        def recurse(expr):
            if isinstance(expr, FieldFilter):
                if expr not in optimized_set:
                    results.append(expr)
            elif isinstance(expr, (AndFilter, OrFilter)) and hasattr(expr, 'filters'):
                for f in expr.filters:
                    recurse(f)
            else:
                results.append(expr)

        recurse(filter_expr)
        return results

    def _sort_by_estimated_cost(self, filters):
        def cost_estimator(filter_):
            if hasattr(filter_, 'strategy'):
                if isinstance(filter_.strategy, ExactMatchingStrategy):
                    return 1
                elif isinstance(filter_.strategy, StartsWithStrategy):
                    return 2
                elif isinstance(filter_.strategy, RegexStrategy):
                    return 10
                elif isinstance(filter_.strategy, FuzzyStrategy):
                    return 20
            if isinstance(filter_, AndFilter):
                return 5
            if isinstance(filter_, OrFilter):
                return 8
            return 5
        return sorted(filters, key=cost_estimator)
