from typing import List, Optional
import ast
from models.function import FunctionSignature, ParameterSignature, FunctionElement
from models.semantic_nodes import ElementType



class ASTParser:
    def parse_file(self, file_path: str) -> List[FunctionElement]:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        ast_tree = ast.parse(source, filename=file_path)
        extractor = CodeElementExtractor(file_path)
        elements = list(extractor.extract_elements(ast_tree).values())
        return elements


class CodeElementExtractor:
    def __init__(self, file_path):
        self.file_path = file_path

    def extract_elements(self, ast_tree: ast.AST):
        visitor = FunctionVisitor(self.file_path)
        visitor.visit(ast_tree)
        return visitor.elements


class FunctionVisitor(ast.NodeVisitor):
    def __init__(self, file_path):
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
        parameters = []  # Assume this is extracted elsewhere
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
            parent_name=(self.current_class if self.current_class else (self.namespace_stack[-2] if len(self.namespace_stack) > 1 else None)),
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