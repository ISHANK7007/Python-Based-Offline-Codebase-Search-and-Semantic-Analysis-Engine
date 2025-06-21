# semantic_indexer/filters.py

from enum import Enum
from typing import Any, List
import re

class MatchType(Enum):
    EXACT = "exact"
    FUZZY = "fuzzy"
    REGEX = "regex"
    STARTSWITH = "startswith"
    ENDSWITH = "endswith"
    CONTAINS = "contains"

class Filter:
    """Base class for all filters."""
    def matches(self, element: Any) -> bool:
        """Return True if the element matches this filter."""
        raise NotImplementedError("Subclasses must implement matches()")

class AttributeFilter(Filter):
    """Matches a given attribute on an element using a specified match strategy."""

    def __init__(self, 
                 attr_name: str, 
                 value: Any, 
                 match_type: MatchType = MatchType.EXACT):
        self.attr_name = attr_name
        self.value = value
        self.match_type = match_type
        self._regex = None

        if self.match_type == MatchType.REGEX:
            try:
                self._regex = re.compile(self.value)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {self.value}") from e

    def matches(self, element: Any) -> bool:
        attr_value = getattr(element, self.attr_name, None)
        if attr_value is None:
            return False

        value_str = str(self.value)
        attr_str = str(attr_value)

        if self.match_type == MatchType.EXACT:
            return attr_value == self.value
        elif self.match_type == MatchType.FUZZY:
            from thefuzz import fuzz
            return fuzz.ratio(attr_str, value_str) >= 70
        elif self.match_type == MatchType.REGEX:
            return bool(self._regex and self._regex.search(attr_str))
        elif self.match_type == MatchType.STARTSWITH:
            return attr_str.startswith(value_str)
        elif self.match_type == MatchType.ENDSWITH:
            return attr_str.endswith(value_str)
        elif self.match_type == MatchType.CONTAINS:
            return value_str in attr_str

        return False

class CompositeFilter(Filter):
    """Combines multiple filters using logical AND or OR."""

    def __init__(self, filters: List[Filter], operator: str = "AND"):
        self.filters = filters
        self.operator = operator.upper()
        if self.operator not in {"AND", "OR"}:
            raise ValueError(f"Unsupported operator: {self.operator}")

    def matches(self, element: Any) -> bool:
        if not self.filters:
            return True
        if self.operator == "AND":
            return all(f.matches(element) for f in self.filters)
        if self.operator == "OR":
            return any(f.matches(element) for f in self.filters)
