import unittest
import ast
import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.semantic_nodes import FunctionElement
from models.enums import ElementType
from semantic.semantic_indexer import SemanticIndexer

class TestGoldenValidation(unittest.TestCase):
    def setUp(self):
        self.indexer = SemanticIndexer()

    def test_function_complexity_enrichment(self):
        source_code = """
def complex_function(data):
    if data:
        for item in data:
            if item.is_valid():
                try:
                    process(item)
                except Exception as e:
                    log(e)
    return data
"""
        ast_node = ast.parse(source_code).body[0]
        element = FunctionElement(
            name="complex_function",
            element_type=ElementType.FUNCTION,
            file_path="mock_file.py",
            line_start=1,
            line_end=10,
            ast_node=ast_node
        )

        # 👇 Manually set id required by SemanticIndexer
        element.id = "func001"

        enriched = self.indexer.process_element(element)
        traits = enriched.semantic_traits.get("complexity", {})

        self.assertEqual(traits.get("cyclomatic_complexity"), 4)
        self.assertEqual(traits.get("branch_count"), 2)
        self.assertEqual(traits.get("loop_count"), 1)
        self.assertEqual(traits.get("exception_handlers"), 1)
        self.assertEqual(traits.get("return_points"), 1)
        self.assertEqual(traits.get("max_nesting"), 3)
        self.assertTrue(traits.get("is_complex"))

        print("✅ Golden traits validated:", traits)

if __name__ == "__main__":
    unittest.main()
