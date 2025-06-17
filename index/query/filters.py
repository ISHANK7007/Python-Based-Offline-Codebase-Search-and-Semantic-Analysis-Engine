# index/query/filters.py

# Base filter interface
class Filter:
    def matches(self, item):
        """Determine whether the item satisfies the filter condition"""
        raise NotImplementedError("Subclasses must implement 'matches'.")


# Logical filter combinators
class AndFilter(Filter):
    def __init__(self, filters):
        self.filters = filters

    def matches(self, item):
        return all(f.matches(item) for f in self.filters)


class OrFilter(Filter):
    def __init__(self, filters):
        self.filters = filters

    def matches(self, item):
        return any(f.matches(item) for f in self.filters)


class NotFilter(Filter):
    def __init__(self, sub_filter):
        self.sub_filter = sub_filter

    def matches(self, item):
        return not self.sub_filter.matches(item)


# Example field-based filter (for extensibility)
class FieldFilter(Filter):
    def __init__(self, field_name, value, strategy=None):
        self.field_name = field_name
        self.value = value
        self.strategy = strategy or ExactMatchingStrategy()

    def matches(self, item):
        field_value = getattr(item, self.field_name, None)
        return self.strategy.match(field_value, self.value)


# Default matching strategies
class MatchingStrategy:
    def match(self, field_value, expected_value):
        raise NotImplementedError("Subclasses must implement 'match'.")


class ExactMatchingStrategy(MatchingStrategy):
    def match(self, field_value, expected_value):
        return field_value == expected_value


class IncludesStrategy(MatchingStrategy):
    def match(self, field_value, expected_value):
        if not isinstance(field_value, str):
            return False
        return expected_value in field_value
