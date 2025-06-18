import hashlib
import json
from typing import Any, Dict, List, Optional, Set, Tuple
import ast

class CodeElementHasher:
    def compute_hash(self, code_element: Any) -> str:
        """Compute a stable version hash for a code element."""
        # Step 1: Create a normalized representation dictionary
        normalized_data = self._create_normalized_representation(code_element)
        
        # Step 2: Convert to a canonical string representation
        canonical_str = json.dumps(normalized_data, sort_keys=True, separators=(',', ':'))
        
        # Step 3: Compute a cryptographic hash
        return hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
    
    def _create_normalized_representation(self, code_element: Any) -> Dict[str, Any]:
        """Create a normalized representation of the code element for hashing."""
        element_type = type(code_element).__name__
        
        # Common properties for all elements
        normalized_data = {
            "type": element_type,
            "file_path": code_element.file_path,
            "line_range": (code_element.start_line, code_element.end_line),
            "name": code_element.name
        }
        
        # Type-specific normalization
        if element_type == "FunctionElement":
            normalized_data.update(self._normalize_function_element(code_element))
        elif element_type == "ClassElement":
            normalized_data.update(self._normalize_class_element(code_element))
        elif element_type == "VariableElement":
            normalized_data.update(self._normalize_variable_element(code_element))
        
        return normalized_data