from typing import List, Dict, Tuple
from models.code_element import BaseCodeElement, CodeElementId
from models.function import FunctionElement

def process_file_incremental(self, file_path: str, elements: List[Dict]) -> Tuple[List[BaseCodeElement], List[CodeElementId]]:
    """
    Process a file incrementally, identifying new, updated, and removed elements.
    Returns a tuple of (processed_elements, removed_element_ids).
    """
    existing_elements = {}
    if file_path in self.files:
        for element_id_str, element in self.files[file_path]["symbols"].items():
            existing_elements[element_id_str] = element

    processed_elements = self.process_file(file_path, elements)

    processed_ids = {str(element.element_id) for element in processed_elements}
    removed_ids = []

    for element_id_str, element in existing_elements.items():
        if element_id_str not in processed_ids:
            removed_ids.append(element.element_id)

    for element_id in removed_ids:
        self.remove_element(element_id)

    return processed_elements, removed_ids


def remove_element(self, element_id: CodeElementId) -> None:
    """Remove an element from all indices."""
    element_id_str = str(element_id)

    # Locate the element via ID
    element = self.registry.get_by_id(element_id)
    if not element:
        return

    file_path = element.file_path
    element_type = element.type.lower()

    # Remove from type-based index
    if element_type in self.by_symbol_type and element_id_str in self.by_symbol_type[element_type]:
        del self.by_symbol_type[element_type][element_id_str]

    # If it's a function, clean role and decorator indices
    if isinstance(element, FunctionElement):
        for role in getattr(element, "semantic_roles", []):
            if role in self.role_index and element in self.role_index[role]:
                self.role_index[role].remove(element)

        for decorator in getattr(element, "decorators", []):
            decorator_name = decorator.name
            if not decorator_name.startswith("@"):
                decorator_name = f"@{decorator_name}"
            if decorator_name in self.decorator_index and element in self.decorator_index[decorator_name]:
                self.decorator_index[decorator_name].remove(element)

    # Remove from file structure
    if file_path in self.files and element_id_str in self.files[file_path]["symbols"]:
        del self.files[file_path]["symbols"][element_id_str]

    # Remove from registry
    self.registry.remove(element_id)
