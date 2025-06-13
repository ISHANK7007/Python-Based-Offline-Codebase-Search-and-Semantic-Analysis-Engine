from typing import Any, Dict, List, Optional, Set, Tuple
from typing import Dict, Any
from index.codebase_index import CodebaseIndex
from models.code_element import CodeElement  # ✅ correct

import json

class CodebaseIndexSerializer:
    """
    Serializer to persist and load CodebaseIndex and its elements.
    Can be extended to support disk storage, JSON lines, or remote sync.
    """

    def __init__(self, index: CodebaseIndex):
        self.index = index

    def to_dict(self) -> Dict[str, Any]:
        # Placeholder for real serialization logic
        return {
            "files": {
                path: {
                    "symbols": {
                        str(el_id): el.to_dict() for el_id, el in data["symbols"].items()
                    }
                }
                for path, data in self.index.files.items()
            }
        }

    def save_to_json(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
    def _normalize_variable_element(self, variable_element: Any) -> Dict[str, Any]:
        """Create a normalized representation of a VariableElement."""
        return {
            "annotation": str(variable_element.annotation) if variable_element.annotation else None,
            "is_constant": getattr(variable_element, "is_constant", False),
            "value_type": type(variable_element.value).__name__ if hasattr(variable_element, "value") else None
        }