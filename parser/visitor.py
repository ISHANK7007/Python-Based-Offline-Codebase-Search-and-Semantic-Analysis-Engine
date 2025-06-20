from typing import List, Optional, Union
import ast
from models.function import FunctionSignature, ParameterSignature, FunctionElement
from models.semantic_nodes import ElementType


class ASTParser(ast.NodeVisitor):
    def __init__(self):
        self.elements = []
        self.file_path = None

    def parse_file(self, file_path: str) -> List[FunctionElement]:
        """Parse and extract function elements from a file path."""
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        ast_tree = ast.parse(source, filename=file_path)
        return self.parse(ast_tree, file_path)

    def parse(self, node: Union[ast.AST, List[ast.AST]], file_path: str) -> List[FunctionElement]:
        """Parse and extract function elements from an AST or list of AST nodes."""
        self.elements = []
        self.file_path = file_path

        if isinstance(node, list):
            for subnode in node:
                if isinstance(subnode, ast.AST):
                    self.visit(subnode)
        elif isinstance(node, ast.AST):
            self.visit(node)
        else:
            raise TypeError(f"Expected ast.AST or list, got: {type(node)}")

        return self.elements


class CodeElementExtractor:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_elements(self, ast_tree: ast.AST):
        visitor = FunctionVisitor(self.file_path)
        visitor.visit(ast_tree)
        return visitor.elements


class FunctionVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.elements = {}
        self.current_class = None
        self.namespace_stack = []
        self.module_path = None

    def visit_FunctionDef(self, node):
        self._visit_func(node, is_async=False)

    def visit_AsyncFunctionDef(self, node):
        self._visit_func(node, is_async=True)

    def _visit_func(self, node, is_async: bool):
        parameters = []  # Extend to extract arguments if needed
        start_line = getattr(node, "lineno", -1)
        end_line = getattr(node, "end_lineno", -1)
        function_element = FunctionElement(
            name=node.name,
            element_type=ElementType.METHOD if self.current_class else ElementType.FUNCTION,
            file_path=self.file_path,
            line_start=start_line,
            line_end=end_line,
            docstring=ast.get_docstring(node),
            decorators=[],
            parent_name=self.current_class or (self.namespace_stack[-2] if len(self.namespace_stack) > 1 else None),
            module_path=self.module_path,
            ast_node=node,
            signature=FunctionSignature(
                parameters=parameters,
                return_type=None,
                is_async=is_async
            ),
            return_annotation=None,
            is_method=bool(self.current_class),
            is_static=False,
            is_class_method=False,
            is_property=False
        )
        self.elements[node.name] = function_element


class OverrideDetectionVisitor(ast.NodeVisitor):
    def __init__(self, indexer):
        self.indexer = indexer

    def analyze(self, element):
        if element.type != 'function' or not hasattr(element, 'parent'):
            return {'is_override': False}

        parent_class = element.parent
        if parent_class.type != 'class':
            return {'is_override': False}

        base_classes = self.get_base_classes(parent_class)
        method_name = element.name

        for base_class in base_classes:
            if self.has_method(base_class, method_name):
                return {
                    'is_override': True,
                    'overrides': f"{base_class.name}.{method_name}",
                    'base_class': base_class.name
                }

        return {'is_override': False}

    def get_base_classes(self, class_element):
        if not hasattr(class_element, 'base_classes'):
            return []
        return [
            self.indexer.class_index[base_name]
            for base_name in class_element.base_classes
            if base_name in self.indexer.class_index
        ]

    def has_method(self, class_element, method_name):
        return any(method.name == method_name for method in getattr(class_element, 'methods', []))
