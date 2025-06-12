import logging
import sys
from pathlib import Path

# Ensure Output_code is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scanner.file_scanner import FileCrawler
from parser.safe_parser import SafeParser
from parser.visitor import ASTParser
from index.indexer import CodebaseIndex
from semantic.semantic_indexer import SemanticIndexer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Entry point for running the full codebase indexing pipeline.
    It performs directory scan, AST parsing, semantic enrichment, and indexing.
    """
    root_directory = Path(__file__).parent / "mockpackage"
    if not root_directory.exists():
        logging.warning(f"Directory not found: {root_directory}. Using current directory instead.")
        root_directory = Path(__file__).parent

    logger.info(f"Scanning Python files in: {root_directory}")

    # Step 1: Crawl all Python files
    crawler = FileCrawler()
    python_files = crawler.scan_directory(str(root_directory))

    # Step 2: Parse Python files into AST
    parser = ASTParser()
    all_elements = {}
    for file_path in python_files:
        file_elements = parser.parse_file(file_path)
        all_elements.update({el.name: el for el in file_elements})

    logger.info(f"Parsed {len(all_elements)} code elements from {len(python_files)} files.")

    # Step 3: Enrich elements with semantic traits
    indexer = SemanticIndexer()
    for el_name, element in all_elements.items():
        enriched = indexer.process_element(element)
        all_elements[el_name] = enriched

    # Step 4: Index the enriched elements
    index = CodebaseIndex()
    for element in all_elements.values():
        index.add_element(element)

    # Step 5: Display semantic traits and search results
    search_term = "parse"
    results = index.search(search_term)
    print(f"\n🔍 Search results for '{search_term}':")
    for res in results:
        print(f"- {res.qualified_name} ({res.element_type})")

    print("\n📌 Semantic trait overview:")
    for name, el in all_elements.items():
        print(f"\n▶ {name}")
        if hasattr(el, "semantic_traits"):
            for trait_key, trait_val in el.semantic_traits.items():
                print(f"  {trait_key}: {trait_val}")
        else:
            print("  (No semantic traits enriched)")


if __name__ == "__main__":
    main()
