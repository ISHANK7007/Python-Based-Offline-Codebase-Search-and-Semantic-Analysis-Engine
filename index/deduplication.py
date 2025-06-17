import ast
import hashlib
from typing import Any, Dict, List

class ElementNormalizer:
    """Normalizes code elements (functions, classes) for deduplication comparison."""

    def _normalize_class_element(self, class_element: Any) -> Dict[str, Any]:
        """Create a normalized representation of a ClassElement."""
        try:
            class_ast = ast.parse(class_element.body).body[0]
        except (SyntaxError, IndexError):
            # Fallback if parsing fails
            return {
                "base_classes": [str(base) for base in class_element.bases],
                "body_hash": hashlib.sha256(class_element.body.encode('utf-8')).hexdigest()
            }

        return {
            "base_classes": [str(base) for base in class_element.bases],
            "decorators": self._normalize_decorators(getattr(class_element, "decorators", [])),
            "method_signatures": self._normalize_method_signatures(class_element),
            "class_variables": self._normalize_class_variables(class_element),
            "ast_structure": self._normalize_class_ast(class_ast),
        }

    def _normalize_method_signatures(self, class_element: Any) -> Dict[str, str]:
        """Normalize method signatures within a class."""
        method_sigs = {}
        for method in getattr(class_element, "methods", []):
            method_sigs[method.name] = self._normalize_signature(method)
        return method_sigs

    def _normalize_class_variables(self, class_element: Any) -> List[Dict[str, Any]]:
        """Normalize class variables."""
        variables = []
        for var in getattr(class_element, "class_variables", []):
            variables.append({
                "name": var.name,
                "annotation": str(var.annotation) if hasattr(var, "annotation") and var.annotation else None,
                "has_value": hasattr(var, "value") and var.value is not None
            })
        return variables

    def _normalize_decorators(self, decorators: List[Any]) -> List[str]:
        """Extract decorator names as strings."""
        return [getattr(decorator, "name", str(decorator)) for decorator in decorators]

    def _normalize_class_ast(self, class_ast_node: ast.AST) -> str:
        """Generate a normalized AST structure string."""
        return ast.dump(class_ast_node)

    def _normalize_signature(self, method: Any) -> str:
        """Simple placeholder normalization of method signature."""
        return f"{method.name}({','.join(str(p) for p in getattr(method, 'parameters', []))})"
