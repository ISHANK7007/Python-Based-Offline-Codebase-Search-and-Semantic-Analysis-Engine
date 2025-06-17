# semantic_indexer/schema.py
from index.query.filters import MatchType
from dataclasses import dataclass
from typing import List

@dataclass
class QueryableField:
    name: str
    type: str
    description: str
    match_types: List[MatchType]

def get_queryable_fields() -> List[QueryableField]:
    return [
        QueryableField(
            name="name",
            type="str",
            description="Name of the code element",
            match_types=[MatchType.EXACT, MatchType.FUZZY, MatchType.REGEX]
        ),
        QueryableField(
            name="docstring",
            type="str",
            description="Docstring content",
            match_types=[MatchType.CONTAINS, MatchType.REGEX]
        ),
        # Add more fields as needed
    ]
