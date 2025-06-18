# Using Typer with Pydantic for field introspection
from typing import List, Optional
import typer
from pydantic import BaseModel, Field
from enum import Enum

class ElementType(str, Enum):
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    ANY = "any"

class MatchType(str, Enum):
    EXACT = "exact"
    FUZZY = "fuzzy"
    REGEX = "regex"
    CONTAINS = "contains"

class CodeElementField(BaseModel):
    """Definition of a queryable field on CodeElement."""
    name: str
    description: str
    type: str
    match_types: List[MatchType] = Field(default_list=[MatchType.EXACT])

# Define queryable fields
QUERYABLE_FIELDS = [
    CodeElementField(
        name="name",
        description="Element name",
        type="str",
        match_types=[MatchType.EXACT, MatchType.FUZZY, MatchType.REGEX, MatchType.CONTAINS]
    ),
    CodeElementField(
        name="docstring",
        description="Element documentation",
        type="str",
        match_types=[MatchType.CONTAINS, MatchType.REGEX]
    ),
    CodeElementField(
        name="element_type",
        description="Element type",
        type="ElementType",
        match_types=[MatchType.EXACT]
    )
]

# Dynamically create CLI options based on queryable fields
app = typer.Typer()

@app.command()
def search(
    query: str = typer.Argument("*", help="Search query expression"),
    limit: int = typer.Option(20, help="Maximum results to return"),
    **kwargs  # Will receive dynamically generated options
):
    """Search for code elements matching criteria."""
    print(f"Query: {query}")
    print(f"Additional filters: {kwargs}")

# Dynamically add options based on queryable fields
def register_field_options():
    # Get the search command function
    search_command = app.registered_commands[0]
    
    # For each field, add options for each supported match type
    for field in QUERYABLE_FIELDS:
        for match_type in field.match_types:
            option_name = f"--{field.name}-{match_type.value}"
            param_name = f"{field.name}_{match_type.value}"
            help_text = f"Filter {field.description} using {match_type.value} matching"
            
            # Add the option to the command
            typer.Option(None, help=help_text)(search_command.callback, param_name)

# Register all field options
register_field_options()

if __name__ == "__main__":
    app()