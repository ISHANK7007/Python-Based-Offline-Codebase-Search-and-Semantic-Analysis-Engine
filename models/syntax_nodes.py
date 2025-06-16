from dataclasses import dataclass
from typing import List, Optional
from models.types import Location  # ✅ Import the Location type

@dataclass
class FunctionNodeInfo:
    name: str
    lineno: int
    col_offset: int
    end_lineno: int
    end_col_offset: int
    bases: List[str]
    decorator_names: List[str]
    args: List[str]
    return_type: Optional[str] = None
    return_annotation_str: Optional[str] = None
    docstring: Optional[str] = None
    is_async: bool = False
    location: Optional[Location] = None  # ✅ Add this field
