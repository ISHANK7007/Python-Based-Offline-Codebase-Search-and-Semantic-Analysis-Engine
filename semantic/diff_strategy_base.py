from abc import ABC, abstractmethod

class DiffStrategy(ABC):
    """Base class for all diffing strategies."""

    @abstractmethod
    def compare(self, element1, element2, context=None):
        """Compare two code elements and return structured diff result."""
        pass

    @abstractmethod
    def match_symbols(self, symbol, index1, index2, threshold=0.65):
        """Try to match a symbol between two indices."""
        pass
