import logging
import sys
from pathlib import Path

# Ensure Output_code is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))


from scanner.file_scanner import FileCrawler
from parser.safe_parser import SafeParser
from parser.visitor import ASTParser
from index.indexer import CodebaseIndex

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Entry point for running the full codebase indexing pipeline.
    It performs directory scan, AST parsing, and indexing of code elements.
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

    # Step 3: Index the elements
    index = CodebaseIndex()
    for element in all_elements.values():
        index.add_element(element)

    # Example query (adjust as needed)
    search_term = "parse"
    results = index.search(search_term)
    print(f"\n🔍 Search results for '{search_term}':")
    print("\nAll parsed elements:")
    for name in all_elements.keys():
        print(f"- {name}")
    for res in results:
        print(f"- {res.qualified_name} ({res.element_type})")


if __name__ == "__main__":
    main()
