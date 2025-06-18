# index/query/includes_strategy.py

from index.query.matching_strategies import MatchingStrategy

class IncludesStrategy(MatchingStrategy):
    def matches(self, field_value, pattern):
        if not isinstance(field_value, str):
            return False
        return pattern.lower() in field_value.lower()
