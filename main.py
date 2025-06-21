import logging
import sys
import argparse
from pathlib import Path

# Extend sys.path to include Output_code root for relative imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Scanner and Parser
from scanner.file_scanner import FileCrawler
from parser.safe_parser import SafeParser
from parser.visitor import ASTParser

# Indexing
from index.codebase_index import CodebaseIndex
from index.serializer import CodebaseIndexSerializer
from index.lazy_registry import LazyLoadedRegistry

# Semantic Processing
from semantic.semantic_indexer import SemanticIndexer
from semantic.call_graph import SemanticVisitorManager

# CLI Query and Output
from index.query.query_engine import QueryEngine
from index.formatter.templates import FormatterTemplates
from cli.cli_filter_parser import build_filter_from_args
from cli.cli_output_args import process_formatting_args

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def setup_cli_parser():
    parser = argparse.ArgumentParser(description="🔍 Offline Codebase Search CLI")

    # Filtering arguments
    parser.add_argument("--name", help="Exact name to match")
    parser.add_argument("--name-regex", help="Regex pattern to match name")
    parser.add_argument("--name-fuzzy", help="Fuzzy string to match name")
    parser.add_argument("--doc-includes", help="Text that should appear in docstring")
    parser.add_argument("--type", help="Element type: function, class, etc.")
    parser.add_argument("--role", help="Semantic role, e.g., entrypoint, utility")
    parser.add_argument("--decorator", help="Decorator to match")

    # Output formatting
    parser.add_argument("--output", "-o", choices=["text", "json", "csv", "yaml", "markdown"], default="text")
    parser.add_argument("--columns", nargs="+", help="Columns to include in the output")
    parser.add_argument("--sort-by", help="Sort results by this field")
    parser.add_argument("--max-width", type=int, help="Maximum column width for text/markdown formats")

    return parser


def main():
    # Default scanning path
    root_directory = Path(__file__).parent / "mockpackage"
    if not root_directory.exists():
        logger.warning(f"[WARN] Directory not found: {root_directory}. Using current directory.")
        root_directory = Path(__file__).parent

    logger.info(f"[INFO] Scanning Python files in: {root_directory}")
    crawler = FileCrawler()
    python_files = crawler.scan_directory(str(root_directory))

    parser = SafeParser()
    visitor = ASTParser()
    code_index = CodebaseIndex()
    all_elements = []

    for file_path in python_files:
        try:
            ast_tree = parser.safe_parse_file(str(file_path))
            if ast_tree:
                elements = visitor.parse(ast_tree, file_path=str(file_path))
                all_elements.extend(elements)
        except Exception as e:
            logger.warning(f"[WARN] Failed to parse {file_path}: {e}")

    logger.info(f"[INFO] Parsed {len(all_elements)} elements from {len(python_files)} files.")

    # Semantic enrichment and analysis
    semantic_indexer = SemanticIndexer()
    semantic_visitor = SemanticVisitorManager(code_index)

    for el in all_elements:
        semantic_indexer.analyze_function_element(el)
        semantic_visitor.analyze_element(el)

    # Register with Lazy Loader for CLI recovery
    serializer = CodebaseIndexSerializer(code_index)
    lazy_registry = LazyLoadedRegistry(serializer)
    for el in all_elements:
        lazy_registry.register(el)

    # CLI Setup and Execution
    cli_parser = setup_cli_parser()
    args = cli_parser.parse_args()
    query_engine = QueryEngine(code_index)
    query_engine.set_formatter(FormatterTemplates.code_review())

    process_formatting_args(args, query_engine)
    filter_expr = build_filter_from_args(args)

    if filter_expr:
        results = query_engine.query(filter_expr)
        print("\n🔎 Query Results:")
        for item in results:
            print(f"- {item.name}  ({item.file_path})")
    else:
        print("⚠️ No valid query provided. Use --help to see options.")


if __name__ == "__main__":
    main()
