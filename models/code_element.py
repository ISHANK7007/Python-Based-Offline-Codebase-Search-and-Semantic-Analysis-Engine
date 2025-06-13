from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import ast
from abc import ABC

from models.types import ElementKind, ElementType


# ✅ Abstract Base for all code elements
class BaseCodeElement(ABC):
    pass


@dataclass
class Location:
    file_path: str
    line: int
    column: int


@dataclass
class FunctionSignature:
    parameters: List[str]
    return_type: Optional[str] = None
    is_async: bool = False


@dataclass
class CodeElement(BaseCodeElement):  # Inherit from BaseCodeElement
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

    @property
    def location(self) -> Location:
        return Location(
            file_path=str(self.file_path),
            line=self.line_start,
            column=0  # Column not tracked in this version
        )


# ✅ Define CodeElementId (if not already defined elsewhere)
@dataclass(frozen=True)
class CodeElementId:
    file_path: str
    element_type: str
    name: str
    start_line: int
    end_line: int
