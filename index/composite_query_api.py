from typing import Optional, List, Any

# Inside class CodebaseIndex:

def find_functions(self, 
                   roles: Optional[List[str]] = None, 
                   decorators: Optional[List[str]] = None,
                   symbol_types: Optional[List[str]] = None) -> List[Any]:
    """Find functions matching multiple criteria"""
    candidate_sets = []

    if roles:
        role_candidates = set()
        for role in roles:
            role_candidates.update(self.role_index.get(role, []))
        candidate_sets.append(role_candidates)

    if decorators:
        decorator_candidates = set()
        for decorator in decorators:
            if not decorator.startswith('@'):
                decorator = f"@{decorator}"
            decorator_candidates.update(self.decorator_index.get(decorator, []))
        candidate_sets.append(decorator_candidates)

    if symbol_types:
        type_candidates = set()
        for symbol_type in symbol_types:
            type_candidates.update(self.by_symbol_type.get(symbol_type, {}).values())
        candidate_sets.append(type_candidates)

    if not candidate_sets:
        return []

    result = candidate_sets[0]
    for candidates in candidate_sets[1:]:
        result = result.intersection(candidates)

    return list(result)


def update_index(self, new_or_modified_elements: List[Any]) -> None:
    """Update the index with new or modified elements."""
    for element in new_or_modified_elements:
        element_id = self._generate_element_id(element)

        if self.has_element_changed(element):
            if element_id in self.element_hashes:
                self._remove_element(element_id)
            self.add_element(element)
