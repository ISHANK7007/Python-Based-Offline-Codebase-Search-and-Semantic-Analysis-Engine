from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import ast

from models.types import ElementKind, ElementType

# ✅ Define Location class
@dataclass
class Location:
    file_path: str
    line: int
    column: int

@dataclass
class FunctionSignature:
    parameters: List[str]
    return_type: Optional[str] = None

@dataclass
class CodeElement:
    """Base class for all code elements found in Python source files."""
    name: str
    element_type: ElementType
    file_path: Path
    line_start: int
    line_end: int
    module_path: str
    signature: FunctionSignature
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    parent_name: Optional[str] = None
    ast_node: Optional[ast.AST] = field(default=None, repr=False)

    # ✅ Add computed location property (optional)
    @property
    def location(self) -> Location:
        return Location(
            file_path=str(self.file_path),
            line=self.line_start,
            column=0  # Column not available in current setup
        )
