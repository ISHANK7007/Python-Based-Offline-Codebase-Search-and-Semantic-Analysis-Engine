import re
import difflib

# Try to import Levenshtein once
try:
    import Levenshtein
    has_levenshtein = True
except ImportError:
    has_levenshtein = False


class MatchingStrategy:
    def matches(self, field_value, pattern):
        raise NotImplementedError("Subclasses must implement matches()")


class ExactMatchingStrategy(MatchingStrategy):
    def matches(self, field_value, pattern):
        return str(field_value) == str(pattern)


class StartsWithStrategy(MatchingStrategy):
    def matches(self, field_value, pattern):
        try:
            return str(field_value).startswith(str(pattern))
        except Exception:
            return False


class RegexStrategy(MatchingStrategy):
    def matches(self, field_value, pattern):
        try:
            return bool(re.search(str(pattern), str(field_value)))
        except (re.error, TypeError):
            return False


class FuzzyStrategy(MatchingStrategy):
    def __init__(self, threshold=0.7):
        self.threshold = threshold

    def matches(self, field_value, pattern):
        a = str(field_value).lower()
        b = str(pattern).lower()

        if has_levenshtein:
            similarity = Levenshtein.ratio(a, b)
        else:
            similarity = difflib.SequenceMatcher(None, a, b).ratio()

        return similarity >= self.threshold
