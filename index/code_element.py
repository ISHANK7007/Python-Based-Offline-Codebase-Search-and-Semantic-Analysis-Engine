from enum import Enum
from typing import List, Optional


class ElementType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    MODULE = "module"
    UNKNOWN = "unknown"


class CodeElement:
    def __init__(
        self,
        name: str,
        element_type: ElementType,
        file_path: str,
        line_start: int,
        line_end: int,
        doc: Optional[str] = None,
        decorators: Optional[List[str]] = None,
        role: Optional[str] = None,
        module_path: Optional[str] = None,
        calls: Optional[List[str]] = None,
        called_by: Optional[List[str]] = None,
        inherits: Optional[List[str]] = None,
        imported_by: Optional[List[str]] = None,
        parent_class: Optional[str] = None,
        parameters: Optional[List[str]] = None,
        return_type: Optional[str] = None
    ):
        self.name = name
        self.type = element_type
        self.file_path = file_path
        self.line_start = line_start
        self.line_end = line_end
        self.doc = doc or ""
        self.decorators = decorators or []
        self.role = role
        self.module_path = module_path
        self.calls = calls or []
        self.called_by = called_by or []
        self.inherits = inherits or []
        self.imported_by = imported_by or []
        self.parent_class = parent_class
        self.parameters = parameters or []
        self.return_type = return_type

    def __repr__(self):
        return f"<{self.type.value}: {self.name} ({self.file_path}:{self.line_start}-{self.line_end})>"
