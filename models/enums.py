# models/enums.py
from enum import Enum, auto

class ElementType(Enum):
    CLASS = auto()
    FUNCTION = auto()
    METHOD = auto()
    IMPORT = auto()
    MODULE = auto()
    VARIABLE = auto()

class ElementKind(Enum):
    DECLARATION = auto()
    DEFINITION = auto()
    USAGE = auto()
    TYPE_HINT = auto()
