import logging
import sys
from pathlib import Path

# Ensure Output_code root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scanner.file_scanner import FileCrawler
from parser.safe_parser import SafeParser
from parser.visitor import ASTParser
from index.codebase_index import CodebaseIndex
from index.serializer import CodebaseIndexSerializer
from index.lazy_registry import LazyLoadedRegistry
from semantic.semantic_indexer import SemanticIndexer
from semantic.call_graph import SemanticVisitorManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Run the full indexing pipeline:
    1. Crawl Python files
    2. Parse files into ASTs and extract code elements
    3. Enrich with semantic traits
    4. Store in index and lazy registry
    5. Display search results
    """
    root_directory = Path(__file__).parent / "mockpackage"
    if not root_directory.exists():
        logger.warning(f"Directory not found: {root_directory}. Using current directory instead.")
        root_directory = Path(__file__).parent

    logger.info(f"🔍 Scanning Python files in: {root_directory}")

    # Step 1: Crawl
    crawler = FileCrawler()
    python_files = crawler.scan_directory(str(root_directory))

    # Step 2: Parse
    parser = SafeParser()
    ast_visitor = ASTParser()
    index = CodebaseIndex()
    all_elements = []

    for path in python_files:
        # Only pass file path to ASTParser
        elements = ast_visitor.parse_file(str(path))
        all_elements.extend(elements)

    logger.info(f"✅ Parsed {len(all_elements)} elements from {len(python_files)} files.")

    # Step 3: Semantic enrichment
    semantic_indexer = SemanticIndexer()
    visitor_manager = SemanticVisitorManager(index)

    for element in all_elements:
        semantic_indexer.analyze_function_element(element)
        visitor_manager.analyze_element(element)

    # Step 4: Lazy registry
    serializer = CodebaseIndexSerializer(index)
    lazy_registry = LazyLoadedRegistry(serializer)
    for el in all_elements:
        lazy_registry.register(el)

    # Step 5: Example query
    search_term = "parse"
    matches = index.search(search_term)
    print(f"\n🔎 Search results for '{search_term}':")
    for m in matches:
        print(f"- {m.qualified_name} ({m.element_type})")

    print("\n📌 Decorator roles summary:")
    for el in all_elements:
        if hasattr(el, "decorator_metadata"):
            print(f"\n▶ {el.qualified_name}")
            for k, v in el.decorator_metadata.items():
                print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
