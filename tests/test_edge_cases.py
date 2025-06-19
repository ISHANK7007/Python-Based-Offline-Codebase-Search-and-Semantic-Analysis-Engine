import unittest
from index.query.field_filter import FieldFilter

from index.query.filters import AndFilter, OrFilter, NotFilter
from index.query.matching_strategies import IncludesStrategy
from index.query.query_engine import QueryEngine
from tests.test_dataset_builder import create_standard_test_dataset
from index.formatter.default_formatter import RawResultsFormatter  # or wherever RawResultsFormatter is defined


class EdgeCaseTests(unittest.TestCase):
    """Tests focusing on edge cases and pathological queries"""

    def setUp(self):
        # Create test data with edge cases
        builder = create_standard_test_dataset()

        # Add empty/special elements
        builder.add_function(
            name="",  # Empty name
            file_path="special/empty.py",
            doc="Function with empty name",
            roles=["special", "empty"]
        )

        builder.add_function(
            name="func_with_special_chars",
            file_path="special/chars.py",
            doc="Function with special characters: @#$%^&*()[]{}",
            roles=["special"]
        )

        # Deep nested filter (alternating AND/OR over 20 layers)
        current = FieldFilter("type", "function")
        for i in range(20):
            if i % 2 == 0:
                current = AndFilter([current, FieldFilter("type", "function")])
            else:
                current = OrFilter([current, FieldFilter("type", "function")])
        self.deep_nested_filter = current

        # Create test index
        self.test_elements = builder.build()
        self.test_index = builder.build_index()

        # Create query engine
        self.query_engine = QueryEngine(self.test_index)
        self.query_engine.formatter = RawResultsFormatter()

    def test_empty_field_values(self):
        """Test filtering with empty field values"""
        empty_name_filter = FieldFilter("name", "")
        results = self.query_engine.query(empty_name_filter)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "")

    def test_special_characters(self):
        """Test filtering with special characters"""
        special_chars_filter = FieldFilter("doc", "@#$%^&*()", strategy=IncludesStrategy())
        results = self.query_engine.query(special_chars_filter)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "func_with_special_chars")

    def test_deep_nested_filter(self):
        """Test very deeply nested filters"""
        try:
            results = self.query_engine.query(self.deep_nested_filter)
            expected = [e for e in self.test_elements if e.type == "function"]
            self.assertEqual(len(results), len(expected))
        except RecursionError:
            self.fail("Deep nested filter caused recursion error")

    def test_contradictory_filters(self):
        """Test filters that are logically contradictory"""
        contradictory = AndFilter([
            FieldFilter("role", "helper"),
            NotFilter(FieldFilter("role", "helper"))
        ])
        results = self.query_engine.query(contradictory)
        self.assertEqual(len(results), 0)

    def test_tautological_filters(self):
        """Test filters that are always true"""
        tautology = OrFilter([
            FieldFilter("role", "helper"),
            NotFilter(FieldFilter("role", "helper"))
        ])
        results = self.query_engine.query(tautology)
        self.assertEqual(len(results), len(self.test_elements))
