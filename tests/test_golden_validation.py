
import unittest
import ast
from models.semantic_nodes import FunctionElement
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
        ast_node = ast.parse(source_code).body[0]  # extract the function node
        element = FunctionElement(
            id="func001",
            name="complex_function",
            type="function",
            ast_node=ast_node,
            file_path="mock_file.py"
        )

        enriched = self.indexer.process_element(element)
        traits = enriched.semantic_traits.get("complexity", {})

        # Assertions against expected golden values
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
