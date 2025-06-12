
from enum import Enum, auto
from dataclasses import dataclass
from pathlib import Path
class ElementKind(Enum):
    MODULE = auto()
    CLASS = auto()
    FUNCTION = auto()


class ElementType(Enum):
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    IMPORT = "import"  # ✅ Add this line to fix the AttributeError


@dataclass
class Location:
    file_path: str
    line: int
    column: int