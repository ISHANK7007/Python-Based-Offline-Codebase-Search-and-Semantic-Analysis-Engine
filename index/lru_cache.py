from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import hashlib

@dataclass(frozen=True)
class CodeElementId:
    """Immutable identifier for a code element."""
    file_path: str
    element_type: str
    name: str
    start_line: int
    end_line: int
    
    def __str__(self) -> str:
        return f"{self.file_path}:{self.element_type}:{self.name}:{self.start_line}-{self.end_line}"

@dataclass
class BaseCodeElement:
    """Base class for all code elements with identity semantics."""
    file_path: str
    name: str
    start_line: int
    end_line: int
    element_hash: str = field(default="", compare=False)
    
    @property
    def element_id(self) -> CodeElementId:
        """Get the unique identifier for this element."""
        return CodeElementId(
            file_path=self.file_path,
            element_type=self.__class__.__name__,
            name=self.name,
            start_line=self.start_line,
            end_line=self.end_line
        )
    
    def __hash__(self) -> int:
        """Define hash based on the element's identity."""
        return hash(self.element_id)
    
    def __eq__(self, other) -> bool:
        """Define equality based on the element's identity."""
        if not isinstance(other, BaseCodeElement):
            return False
        return self.element_id == other.element_id