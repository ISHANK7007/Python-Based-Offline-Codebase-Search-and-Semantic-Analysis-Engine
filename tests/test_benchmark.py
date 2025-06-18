from typing import Any, Type
from models.code_element import BaseCodeElement, CodeElementId
from index.serializer import CodebaseIndexSerializer
from index.lazy_registry import LazyLoadedRegistry

class ElementProxy:
    """Proxy object that loads the real element on demand."""

    def __init__(self, element_id: CodeElementId, element_hash: str, element_type: str,
                 serializer: CodebaseIndexSerializer, registry: LazyLoadedRegistry):
        self._element_id = element_id
        self._element_hash = element_hash
        self._element_type = element_type
        self._serializer = serializer
        self._registry = registry
        self._real_element: BaseCodeElement | None = None

    def __getattr__(self, name: str) -> Any:
        """Transparently load the real element when an attribute is accessed."""
        if self._real_element is None:
            self._load_real_element()

        if self._real_element is None:
            raise AttributeError(f"Failed to load element {self._element_id}")

        return getattr(self._real_element, name)

    def _load_real_element(self) -> None:
        """Load the real element from storage."""
        self._real_element = self._registry.get_by_id(self._element_id)

    @property
    def element_id(self) -> CodeElementId:
        """The element ID is always available without loading."""
        return self._element_id

    @property
    def element_hash(self) -> str:
        """The element hash is always available without loading."""
        return self._element_hash

    @property
    def __class__(self) -> Type:
        """Make isinstance() checks work by delegating to the real element."""
        if self._real_element is None:
            candidate_class = globals().get(self._element_type)
            return candidate_class if candidate_class else BaseCodeElement
        return self._real_element.__class__

    def __eq__(self, other: Any) -> bool:
        """Compare based on element_id without loading."""
        if isinstance(other, ElementProxy):
            return self._element_id == other._element_id
        if isinstance(other, BaseCodeElement):
            return self._element_id == other.element_id
        return False

    def __hash__(self) -> int:
        """Hash based on element_id without loading."""
        return hash(self._element_id)
