
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import ast

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FunctionSignature:
    parameters: List[str]
    return_type: Optional[str] = None

from models.types import ElementKind, ElementType

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
