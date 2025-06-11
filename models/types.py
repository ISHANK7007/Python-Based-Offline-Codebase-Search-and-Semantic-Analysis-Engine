
from enum import Enum, auto

class ElementKind(Enum):
    MODULE = auto()
    CLASS = auto()
    FUNCTION = auto()


class ElementType(Enum):
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    IMPORT = "import"  # ✅ Add this line to fix the AttributeError

