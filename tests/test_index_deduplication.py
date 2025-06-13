from typing import Dict, Optional
from models.code_element import BaseCodeElement, CodeElementId  # adjust path as needed
from index.element_hasher import CodeElementHasher  # adjust path if needed

class ElementRegistry:
    """Registry to manage unique code elements and their hashes."""

    def __init__(self):
        self._elements_by_id: Dict[CodeElementId, BaseCodeElement] = {}
        self._elements_by_hash: Dict[str, BaseCodeElement] = {}
        self._hasher = CodeElementHasher()

    def register(self, element: BaseCodeElement) -> BaseCodeElement:
        """
        Register an element, computing its hash if needed.
        Returns the canonical instance (either the existing one or the newly registered one).
        """
        if element.element_id in self._elements_by_id:
            return self._elements_by_id[element.element_id]

        if not getattr(element, "element_hash", None):
            element.element_hash = self._hasher.compute_hash(element)

        if element.element_hash in self._elements_by_hash:
            existing = self._elements_by_hash[element.element_hash]
            print(f"Note: Different elements with same hash: {element.element_id} and {existing.element_id}")

        self._elements_by_id[element.element_id] = element
        self._elements_by_hash[element.element_hash] = element

        return element

    def get_by_id(self, element_id: CodeElementId) -> Optional[BaseCodeElement]:
        """Get an element by its ID."""
        return self._elements_by_id.get(element_id)

    def get_by_hash(self, element_hash: str) -> Optional[BaseCodeElement]:
        """Get an element by its hash."""
        return self._elements_by_hash.get(element_hash)

    def contains(self, element: BaseCodeElement) -> bool:
        """Check if the registry contains this element."""
        return element.element_id in self._elements_by_id

    def remove(self, element_id: CodeElementId) -> None:
        """Remove an element from the registry."""
        if element_id in self._elements_by_id:
            element = self._elements_by_id[element_id]
            self._elements_by_hash.pop(element.element_hash, None)
            self._elements_by_id.pop(element_id, None)

    def clear(self) -> None:
        """Clear all elements from the registry."""
        self._elements_by_id.clear()
        self._elements_by_hash.clear()
