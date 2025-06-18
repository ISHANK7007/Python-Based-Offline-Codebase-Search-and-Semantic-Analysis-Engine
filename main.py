import logging
import sys
import argparse
from pathlib import Path

# Extend sys.path to include Output_code root
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Core pipeline imports
from scanner.file_scanner import FileCrawler
from parser.safe_parser import SafeParser
from parser.visitor import ASTParser
from index.codebase_index import CodebaseIndex
from index.serializer import CodebaseIndexSerializer
from index.lazy_registry import LazyLoadedRegistry

# Semantic enrichment
from semantic.semantic_indexer import SemanticIndexer
from semantic.call_graph import SemanticVisitorManager

# Query engine and formatter
from index.query.query_engine import QueryEngine
from index.formatter.templates import FormatterTemplates

# CLI parsing and output formatting
from cli.cli_filter_parser import build_filter_from_args
from cli.cli_output_args import process_formatting_args

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


def setup_cli_parser():
    parser = argparse.ArgumentParser(description="Offline Codebase Search CLI")

    # Query filters
    parser.add_argument("--name", help="Exact name match")
    parser.add_argument("--name-regex", help="Name match using regex")
    parser.add_argument("--name-fuzzy", help="Fuzzy name match")
    parser.add_argument("--doc-includes", help="Substring must appear in docstring")
    parser.add_argument("--type", help="Element type")
    parser.add_argument("--role", help="Semantic role (e.g. entrypoint)")
    parser.add_argument("--decorator", help="Decorator name to match")

    # Output formatting
    parser.add_argument("--output", "-o", choices=["text", "json", "csv", "yaml", "markdown"], default="text")
    parser.add_argument("--columns", nargs="+", help="List of columns to include")
    parser.add_argument("--sort-by", help="Sort results by this field")
    parser.add_argument("--max-width", type=int, help="Maximum column width")

    return parser


def main():
    root_directory = Path(__file__).parent / "mockpackage"
    if not root_directory.exists():
        logger.warning(f"Directory not found: {root_directory}. Using current directory instead.")
        root_directory = Path(__file__).parent

    logger.info(f"[INFO] Scanning Python files in: {root_directory}")
    crawler = FileCrawler()
    python_files = crawler.scan_directory(str(root_directory))

    parser = SafeParser()
    ast_visitor = ASTParser()
    index = CodebaseIndex()
    all_elements = []

    for path in python_files:
        try:
            ast_node = parser.safe_parse_file(str(path))
            if ast_node:
                elements = ast_visitor.visit(ast_node, file_path=str(path))
                all_elements.extend(elements)
        except Exception as e:
            logger.warning(f"Failed to parse {path}: {e}")

    logger.info(f"[INFO] Parsed {len(all_elements)} elements from {len(python_files)} files.")

    # Semantic enrichment
    semantic_indexer = SemanticIndexer()
    visitor_manager = SemanticVisitorManager(index)

    for element in all_elements:
        semantic_indexer.analyze_function_element(element)
        visitor_manager.analyze_element(element)

    # Lazy registry
    serializer = CodebaseIndexSerializer(index)
    lazy_registry = LazyLoadedRegistry(serializer)
    for el in all_elements:
        lazy_registry.register(el)

    # Query engine
    query_engine = QueryEngine(index)
    query_engine.set_formatter(FormatterTemplates.code_review())

    # CLI
    cli_parser = setup_cli_parser()
    args = cli_parser.parse_args()
    process_formatting_args(args, query_engine)

    filter_expr = build_filter_from_args(args)

    if filter_expr:
        results = query_engine.query(filter_expr)
        print("\n🔎 Query Results:")
        for item in results:
            print(f"- {item.name}  ({item.file_path})")
    else:
        print("⚠️ No valid query provided.")


if __name__ == "__main__":
    main()
