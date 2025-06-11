# models/base.py
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from pathlib import Path


class ElementType(Enum):
    """Types of code elements that can be indexed."""
    MODULE = auto()
    CLASS = auto()
    FUNCTION = auto()
    METHOD = auto()
    IMPORT = auto()
    VARIABLE = auto()
    EXPRESSION = auto()


class ElementKind(Enum):
    """More specific classification of code elements."""
    # Module kinds
    PACKAGE = auto()
    MODULE = auto()
    
    # Class kinds
    CLASS = auto()
    DATACLASS = auto()
    ENUM = auto()
    EXCEPTION = auto()
    NAMEDTUPLE = auto()
    
    # Function kinds
    FUNCTION = auto()
    METHOD = auto()
    CLASSMETHOD = auto()
    STATICMETHOD = auto()
    PROPERTY = auto()
    CONSTRUCTOR = auto()
    
    # Import kinds
    IMPORT = auto()
    FROM_IMPORT = auto()
    
    # Variable kinds
    CONSTANT = auto()
    VARIABLE = auto()
    INSTANCE_VARIABLE = auto()
    CLASS_VARIABLE = auto()


@dataclass
class Location:
    """Represents a location in source code."""
    file_path: Path
    line_start: int
    line_end: int
    column_start: Optional[int] = None
    column_end: Optional[int] = None
    
    def __str__(self) -> str:
        """String representation of the location."""
        if self.column_start is not None and self.column_end is not None:
            return f"{self.file_path}:{self.line_start}:{self.column_start}-{self.line_end}:{self.column_end}"
        return f"{self.file_path}:{self.line_start}-{self.line_end}"


@dataclass
class BaseModel:
    """Base class for all models."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        raise NotImplementedError("Subclasses must implement to_dict")