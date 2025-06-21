from typing import List, Optional, Dict, Any
import typer
from enum import Enum
from pathlib import Path
import json
import yaml

from index.codebase_index import CodebaseIndex
from index.query.query_engine import QueryEngine
from index.query.filters import AttributeFilter, CompositeFilter, MatchType
from index.query.query_parser import QueryParser

app = typer.Typer()

# Shared context
class AppContext:
    def __init__(self):
        self.codebase_index = None
        self.query_engine = None

context = AppContext()

# Enum for CLI typing
class ElementType(str, Enum):
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    ANY = "any"

@app.callback()
def main(
    codebase_dir: Path = typer.Option(Path.cwd(), help="Root directory of the codebase"),
    index_path: Optional[Path] = typer.Option(None, help="Path to a pre-built index file"),
    debug: bool = typer.Option(False, help="Enable debug mode")
):
    """Semantic code analysis and querying tool."""
    try:
        if index_path and index_path.exists():
            context.codebase_index = CodebaseIndex.load(index_path)
        else:
            context.codebase_index = CodebaseIndex(codebase_dir).build()

        context.query_engine = QueryEngine(context.codebase_index)
    except Exception as e:
        raise typer.Exit(f"Failed to initialize index: {e}")

@app.command()
def search(
    query: str = typer.Argument("*", help="Search query expression"),
    element_type: Optional[ElementType] = typer.Option(None, "--type", "-t"),
    role: Optional[str] = typer.Option(None, "--role", "-r"),
    decorator: Optional[str] = typer.Option(None, "--decorator", "-d"),
    name: Optional[str] = typer.Option(None, "--name", "-n"),
    name_fuzzy: Optional[str] = typer.Option(None, "--name-fuzzy"),
    name_regex: Optional[str] = typer.Option(None, "--name-regex"),
    doc_regex: Optional[str] = typer.Option(None, "--doc-regex"),
    doc_contains: Optional[str] = typer.Option(None, "--doc-contains"),
    limit: int = typer.Option(20, "--limit", "-l", min=1, max=1000),
    format: str = typer.Option("text", "--format", "-f")
):
    """Search for code elements matching specific criteria."""
    if not context.query_engine:
        raise typer.BadParameter("Query engine not initialized")

    filters = []

    if element_type and element_type != ElementType.ANY:
        filters.append(AttributeFilter("element_type", element_type.value))
    if role:
        filters.append(AttributeFilter("semantic_role", role))
    if decorator:
        filters.append(AttributeFilter("decorators", decorator, MatchType.CONTAINS))
    if name:
        filters.append(AttributeFilter("name", name))
    if name_fuzzy:
        filters.append(AttributeFilter("name", name_fuzzy, MatchType.FUZZY))
    if name_regex:
        filters.append(AttributeFilter("name", name_regex, MatchType.REGEX))
    if doc_regex:
        filters.append(AttributeFilter("docstring", doc_regex, MatchType.REGEX))
    if doc_contains:
        filters.append(AttributeFilter("docstring", doc_contains, MatchType.CONTAINS))
    if query and query != "*":
        filters.append(QueryParser.parse_expression(query))

    filter_obj = CompositeFilter(filters)
    results = context.query_engine.search(filter=filter_obj, limit=limit)

    if format == "json":
        print(json.dumps([r.to_dict() for r in results], indent=2))
    elif format == "yaml":
        print(yaml.dump([r.to_dict() for r in results]))
    else:
        if not results:
            print("No results found.")
        for i, r in enumerate(results, 1):
            print(f"[{i}] {r.name} ({r.element_type})")
            print(f"    Path: {r.file_path}:{r.line_number}")
            if r.semantic_role:
                print(f"    Role: {r.semantic_role}")
            if r.decorators:
                print(f"    Decorators: {', '.join(r.decorators)}")
            score = getattr(r, "relevance_score", 1.0)
            print(f"    Score: {score:.2f}\n")

@app.command()
def summarize(
    path: Optional[Path] = typer.Option(None, "--path", "-p"),
    depth: int = typer.Option(2, "--depth", "-d", min=1, max=10),
    include_roles: bool = typer.Option(False, "--include-roles"),
    include_relationships: bool = typer.Option(False, "--include-relationships"),
    format: str = typer.Option("text", "--format", "-f")
):
    """Generate a summary of code structure and relationships."""
    if not context.query_engine:
        raise typer.BadParameter("Query engine not initialized")

    target_path = path or Path.cwd()
    summary = context.query_engine.generate_summary(
        path=target_path,
        depth=depth,
        include_roles=include_roles,
        include_relationships=include_relationships
    )

    if format == "json":
        print(json.dumps(summary.to_dict(), indent=2))
    elif format == "yaml":
        print(yaml.dump(summary.to_dict()))
    elif format == "markdown":
        print(summary.to_markdown())
    else:
        print(summary.to_text())

@app.command()
def describe(
    path: Optional[Path] = typer.Option(None, "--path", "-p"),
    symbol: Optional[str] = typer.Option(None, "--symbol", "-s"),
    show_source: bool = typer.Option(False, "--show-source"),
    show_callers: bool = typer.Option(False, "--show-callers"),
    show_callees: bool = typer.Option(False, "--show-callees"),
    format: str = typer.Option("text", "--format", "-f")
):
    """Provide detailed description of a specific code element."""
    if not context.query_engine:
        raise typer.BadParameter("Query engine not initialized")

    if not path and not symbol:
        raise typer.BadParameter("Either --path or --symbol is required")

    element = context.codebase_index.get_by_path(path) if path else context.codebase_index.get_by_symbol(symbol)

    if not element:
        raise typer.BadParameter("Could not find the specified code element")

    description = context.query_engine.generate_description(
        element=element,
        include_source=show_source,
        include_callers=show_callers,
        include_callees=show_callees
    )

    if format == "json":
        print(json.dumps(description.to_dict(), indent=2))
    elif format == "yaml":
        print(yaml.dump(description.to_dict()))
    elif format == "markdown":
        print(description.to_markdown())
    else:
        print(description.to_text())

@app.command("fields")
def list_fields():
    """List all queryable fields and their supported match types."""
    from index.query.schema import get_queryable_fields

    fields = get_queryable_fields()
    print("Available query fields:\n======================")

    for field in fields:
        print(f"\n{field.name}: {field.type}")
        print(f"  Description: {field.description}")
        print(f"  Match types: {', '.join(m.value for m in field.match_types)}")
        print("  CLI flags:")
        for match_type in field.match_types:
            print(f"    --{field.name}-{match_type.value}")

if __name__ == "__main__":
    app()
