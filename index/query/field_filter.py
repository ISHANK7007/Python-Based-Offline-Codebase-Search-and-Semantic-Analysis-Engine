from index.query.matching_strategies import ExactMatchingStrategy
from index.query.filters import Filter  # if Filter is defined separately

class FieldFilter(Filter):
    def __init__(self, field_name, value, strategy=None):
        if strategy is None:
            strategy = ExactMatchingStrategy()

        self.field_name = field_name
        self.value = value
        self.strategy = strategy

    def matches(self, item):
        if not hasattr(item, self.field_name):
            return False

        field_value = getattr(item, self.field_name)
        if field_value is None:
            return False

        try:
            return self.strategy.matches(field_value, self.value)
        except Exception:
            return False
