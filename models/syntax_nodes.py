
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FunctionNodeInfo:
    name: str
    lineno: int
    col_offset: int
    end_lineno: int
    end_col_offset: int
    bases: List[str]
    decorators: List[str]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
