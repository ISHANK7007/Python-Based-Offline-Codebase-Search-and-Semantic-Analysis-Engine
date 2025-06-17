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

@dataclass(frozen=True)
class CodeElementId:
    file_path: str
    element_type: str
    name: str
    start_line: int
    end_line: int

    def __str__(self):
        return f"{self.element_type}:{self.name}@{self.file_path}:{self.start_line}-{self.end_line}"
