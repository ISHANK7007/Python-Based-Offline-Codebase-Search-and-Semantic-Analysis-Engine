from typing import Dict
from models.code_element import BaseCodeElement

class ElementRegistry:
    """
    Base class for registries that store CodeElements by ID and hash.
    Provides common structure for derived registries like LazyLoadedRegistry.
    """

    def __init__(self):
        self._elements_by_id: Dict[str, BaseCodeElement] = {}
        self._elements_by_hash: Dict[str, BaseCodeElement] = {}

    def clear(self) -> None:
        """Clear all elements from the registry."""
        self._elements_by_id.clear()
        self._elements_by_hash.clear()

    def size(self) -> int:
        """Return the number of elements currently registered."""
        return len(self._elements_by_id)
