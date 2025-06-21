from typing import Any
from models.function import FunctionElement
from models.code_element import ClassElement
from index.element_registry import ElementRegistry
from index.element_hasher import CodeElementHasher

class CodeElementFactory:
    """Factory for creating code elements with de-duplication."""

    def __init__(self, registry: ElementRegistry):
        self.registry = registry
        self.hasher = CodeElementHasher()

    def create_function_element(self, file_path: str, name: str, start_line: int, end_line: int,
                                body: str, **kwargs: Any) -> FunctionElement:
        """Create or retrieve a FunctionElement."""
        temp_element = FunctionElement(
            file_path=file_path,
            name=name,
            start_line=start_line,
            end_line=end_line,
            body=body,
            **kwargs
        )

        # Try ID-based retrieval
        existing = self.registry.get_by_id(temp_element.element_id)
        if existing:
            return existing

        # Compute hash and register
        temp_element.element_hash = self.hasher.compute_hash(temp_element)
        return self.registry.register(temp_element)

    def create_class_element(self, file_path: str, name: str, start_line: int, end_line: int,
                             body: str, **kwargs: Any) -> ClassElement:
        """Create or retrieve a ClassElement."""
        temp_element = ClassElement(
            file_path=file_path,
            name=name,
            start_line=start_line,
            end_line=end_line,
            body=body,
            **kwargs
        )

        existing = self.registry.get_by_id(temp_element.element_id)
        if existing:
            return existing

        temp_element.element_hash = self.hasher.compute_hash(temp_element)
        return self.registry.register(temp_element)

    # You can add similar methods for ModuleElement, VariableElement, etc.
