# tests/test_dataset_builder.py

from index.code_element import CodeElement, ElementType
from index.codebase_index import CodebaseIndex


class TestDatasetBuilder:
    """Utility class to construct controlled test datasets for query engine testing."""

    def __init__(self):
        self.elements = []

    def add_function(self, name, file_path, doc="", roles=None, decorators=None):
        self.elements.append(CodeElement(
            name=name,
            element_type=ElementType.FUNCTION,
            file_path=file_path,
            line_start=1,
            line_end=10,
            docstring=doc,
            decorators=decorators or [],
            role=roles[0] if roles else None,
            roles=roles or [],
            type="function",
        ))

    def add_class(self, name, file_path, doc="", roles=None):
        self.elements.append(CodeElement(
            name=name,
            element_type=ElementType.CLASS,
            file_path=file_path,
            line_start=1,
            line_end=20,
            docstring=doc,
            role=roles[0] if roles else None,
            roles=roles or [],
            type="class",
        ))

    def build(self):
        """Return raw list of elements (for direct assertions)"""
        return self.elements

    def build_index(self):
        """Build a CodebaseIndex from current test elements"""
        index = CodebaseIndex()
        for element in self.elements:
            index.add_element(element)
        return index


def create_standard_test_dataset():
    """Helper function to create a reusable test dataset builder"""
    return TestDatasetBuilder()
