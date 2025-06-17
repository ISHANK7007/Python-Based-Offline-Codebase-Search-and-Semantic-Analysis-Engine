import ast
from typing import Dict, List, Set, Any, Optional

class SemanticVisitorManager:
    """
    Manages semantic visitors and dispatches them to elements.
    Allows AST reuse and multi-visitor execution.
    """

    def __init__(self, indexer: Any):
        self.indexer = indexer
        self.visitors: Dict[str, Any] = {}  # visitor_name -> visitor_instance

    def register_visitor(self, name: str, visitor_class: type, **kwargs):
        """Register a new visitor class under a unique name."""
        self.visitors[name] = visitor_class(self.indexer, **kwargs)

    def analyze_element(self, element: Any, visitor_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run registered visitors on an AST-backed element."""
        if not hasattr(element, 'ast_node'):
            try:
                if element.type == 'function':
                    element.ast_node = ast.parse(element.body).body[0]
                elif element.type == 'class':
                    element.ast_node = ast.parse(element.definition).body[0]
                elif element.type == 'module':
                    element.ast_node = ast.parse(element.source)
                else:
                    return {}
            except SyntaxError:
                return {'error': 'Syntax error in parsing'}

        active_visitors = self.visitors
        if visitor_names:
            active_visitors = {name: self.visitors[name] for name in visitor_names if name in self.visitors}

        results = {}
        for name, visitor in active_visitors.items():
            results[name] = visitor.analyze(element)

        return results


def get_affected_elements(dependency_graph: Dict[str, Set[str]], changed_element_id: str) -> Set[str]:
    """
    Return all elements that directly depend on a changed element.
    Useful for incremental re-analysis or invalidation.
    """
    return dependency_graph.get(changed_element_id, set())
