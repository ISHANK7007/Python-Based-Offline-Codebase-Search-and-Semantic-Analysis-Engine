import ast
from models.code_element import CodeElement  # Ensure this path is correct

def visit_FunctionDef(self, node):
    """Visit a function and convert it into a CodeElement with Git metadata."""
    
    def safe_return_type(node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{safe_return_type(node.value)}.{node.attr}"
        else:
            return None

    def extract_decorator_name(decorator):
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{extract_decorator_name(decorator.value)}.{decorator.attr}"
        else:
            return "<unknown>"

    element = CodeElement(
        name=node.name,
        parameters=[arg.arg for arg in node.args.args],
        returns=safe_return_type(node.returns),
        docstring=ast.get_docstring(node),
        decorators=[extract_decorator_name(d) for d in node.decorator_list],
        line_start=node.lineno,
        line_end=getattr(node, 'end_lineno', node.lineno),
        file_path=self.current_file,
        type="function"
    )

    # Attach Git metadata if applicable
    element.git_metadata = self.get_git_metadata(
        self.current_file,
        node.lineno,
        getattr(node, 'end_lineno', node.lineno)
    )

    return element
