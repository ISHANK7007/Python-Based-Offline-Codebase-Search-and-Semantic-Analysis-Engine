from typing import Optional, List, Set
from models.code_element import BaseCodeElement, CodeElementId  # Assumed structure
from index.serializer import CodebaseIndexSerializer
from index.element_hasher import CodeElementHasher
from index.element_registry import ElementRegistry  # Assuming you have this base class

class LazyLoadedRegistry(ElementRegistry):
    """Registry that lazily loads elements from serialized storage."""

    def __init__(self, serializer: CodebaseIndexSerializer, validate_hashes: bool = True):
        super().__init__()
        self.serializer = serializer
        self.validate_hashes = validate_hashes
        self._loaded_files: Set[str] = set()
        self._hasher = CodeElementHasher()  # 🔧 Fixed: Initialize hasher
        self._elements_by_id: dict[str, BaseCodeElement] = {}
        self._elements_by_hash: dict[str, BaseCodeElement] = {}

    def get_by_id(self, element_id: CodeElementId) -> Optional[BaseCodeElement]:
        """Get an element by ID, loading it if necessary."""
        if element_id in self._elements_by_id:
            return self._elements_by_id[element_id]

        element = self.serializer.load_element(element_id)
        if element:
            if self.validate_hashes:
                current_hash = self._hasher.compute_hash(element)
                if current_hash != getattr(element, "element_hash", ""):
                    print(f"⚠️ Hash mismatch for {element_id}. Expected {element.element_hash}, got {current_hash}")

            self._elements_by_id[element_id] = element
            self._elements_by_hash[element.element_hash] = element

        return element

    def is_loaded(self, element_id: CodeElementId) -> bool:
        """Check if an element is already loaded."""
        return element_id in self._elements_by_id

    def load_file(self, file_path: str) -> List[BaseCodeElement]:
        """Load all elements from a file if not already loaded."""
        if file_path in self._loaded_files:
            return [e for e in self._elements_by_id.values() if e.file_path == file_path]

        elements = self.serializer.load_file_elements(file_path)
        for element in elements:
            if self.validate_hashes:
                current_hash = self._hasher.compute_hash(element)
                if current_hash != getattr(element, "element_hash", ""):
                    print(f"⚠️ Hash mismatch for {element.element_id}. Expected {element.element_hash}, got {current_hash}")

            self._elements_by_id[element.element_id] = element
            self._elements_by_hash[element.element_hash] = element

        self._loaded_files.add(file_path)
        return elements
