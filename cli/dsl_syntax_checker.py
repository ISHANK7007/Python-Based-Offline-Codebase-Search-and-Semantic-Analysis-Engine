# semantic_indexer/schema.py
from typing import List, Set, Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field

class MatchType(str, Enum):
    EXACT = "exact"
    FUZZY = "fuzzy"
    REGEX = "regex"
    CONTAINS = "contains"
    STARTSWITH = "startswith"
    ENDSWITH = "endswith"

class QueryableField(BaseModel):
    """Definition of a queryable field on CodeElement."""
    name: str
    description: str
    type: str
    match_types: List[MatchType] = Field(default_factory=lambda: [MatchType.EXACT])
    examples: List[str] = Field(default_factory=list)

# Define the schema for CodeElement fields
SCHEMA = {
    "name": QueryableField(
        name="name",
        description="Element name (function, class, variable name)",
        type="str",
        match_types=[
            MatchType.EXACT, MatchType.FUZZY, 
            MatchType.REGEX, MatchType.CONTAINS,
            MatchType.STARTSWITH, MatchType.ENDSWITH
        ],
        examples=["search", "Controller", "get*"]
    ),
    "element_type": QueryableField(
        name="element_type",
        description="Type of code element",
        type="str",
        match_types=[MatchType.EXACT],
        examples=["function", "class", "module"]
    ),
    "file_path": QueryableField(
        name="file_path",
        description="Relative path to the file containing the element",
        type="Path",
        match_types=[
            MatchType.EXACT, MatchType.CONTAINS, 
            MatchType.REGEX, MatchType.STARTSWITH,
            MatchType.ENDSWITH
        ],
        examples=["models.py", "api/*.py"]
    ),
    "docstring": QueryableField(
        name="docstring",
        description="Element documentation string",
        type="str",
        match_types=[MatchType.CONTAINS, MatchType.REGEX],
        examples=["HTTP response", "Returns a.*object"]
    ),
    "semantic_role": QueryableField(
        name="semantic_role",
        description="Semantic role of the element",
        type="str",
        match_types=[MatchType.EXACT, MatchType.CONTAINS],
        examples=["api_handler", "data_model"]
    ),
    "decorators": QueryableField(
        name="decorators",
        description="Decorators applied to the element",
        type="List[str]",
        match_types=[MatchType.CONTAINS, MatchType.EXACT],
        examples=["route", "@login_required"]
    ),
    "parameters": QueryableField(
        name="parameters",
        description="Function parameters",
        type="List[str]",
        match_types=[MatchType.CONTAINS],
        examples=["request", "user_id"]
    ),
    "return_type": QueryableField(
        name="return_type",
        description="Function return type annotation",
        type="str",
        match_types=[MatchType.EXACT, MatchType.CONTAINS],
        examples=["Response", "List[User]"]
    ),
    "line_count": QueryableField(
        name="line_count",
        description="Number of lines in the element",
        type="int",
        match_types=[MatchType.EXACT],
        examples=["5", ">10", "<50"]
    )
}

def get_queryable_fields() -> List[QueryableField]:
    """Get all queryable fields."""
    return list(SCHEMA.values())

def get_field(name: str) -> Optional[QueryableField]:
    """Get a field by name."""
    return SCHEMA.get(name)