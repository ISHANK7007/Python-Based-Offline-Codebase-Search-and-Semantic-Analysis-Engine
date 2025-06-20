import unittest
import sys
from pathlib import Path

# Fix import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.function import FunctionElement
from models.enums import ElementType
from semantic.semantic_indexer import SemanticIndexer

# Stub class to fulfill signature requirement
class DummySignature:
    def __init__(self):
        self.parameters = []
        self.return_type = None
        self.is_async = False


class TestSemanticIndexer(unittest.TestCase):

    def create_mock_function(self, name):
        func = FunctionElement(
            name=name,
            element_type=ElementType.FUNCTION,
            file_path="mock_file.py",
            line_start=1,
            line_end=2,
            docstring="mock doc",
            decorators=[],
            parent_name=None,
            module_path="mock.module",
            signature=DummySignature()
        )
        func.calls = []
        func.called_by = []
        print(f"[MOCK CREATED] Function: {name}")
        return func

    def test_process_element_basic_function(self):
        print("\n[TEST] test_process_element_basic_function")
        indexer = SemanticIndexer()
        func = self.create_mock_function("foo")
        enriched = indexer.process_element(func)

        expected_key = "mock.module:foo"
        print(f"[CHECK] Enriched Qualified Name: {enriched.qualified_name}")
        self.assertIn(expected_key, indexer.elements_by_id)
        self.assertEqual(enriched.name, "foo")
        self.assertEqual(enriched.calls, [])
        self.assertTrue(hasattr(enriched, "called_by"))
        print("[PASS] test_process_element_basic_function ✅")

    def test_relationship_resolution_with_calls(self):
        print("\n[TEST] test_relationship_resolution_with_calls")
        indexer = SemanticIndexer()
        func_a = self.create_mock_function("caller")
        func_b = self.create_mock_function("callee")

        func_a.calls = ["callee"]
        func_b.called_by.append(func_a)

        indexer.index_element(func_b)
        indexer.function_index = {"callee": func_b}
        indexer.process_element(func_a)

        self.assertIn(func_a, func_b.called_by)
        print("[PASS] test_relationship_resolution_with_calls ✅")

    def test_pending_relationship_resolution(self):
        print("\n[TEST] test_pending_relationship_resolution")
        indexer = SemanticIndexer()
        caller = self.create_mock_function("early_func")
        caller.calls = ["late_func"]
        indexer.process_element(caller)

        callee = self.create_mock_function("late_func")
        callee.called_by.append(caller)
        indexer.process_element(callee)

        self.assertIn(caller, callee.called_by)
        print("[PASS] test_pending_relationship_resolution ✅")

    def test_process_stream_multiple(self):
        print("\n[TEST] test_process_stream_multiple")
        indexer = SemanticIndexer()
        functions = [self.create_mock_function(f"func_{i}") for i in range(5)]
        processed = indexer.process_stream(functions)

        self.assertEqual(len(processed), 5)
        self.assertEqual(len(indexer.elements_by_id), 5)
        print("[PASS] test_process_stream_multiple ✅")


if __name__ == "__main__":
    unittest.main()
