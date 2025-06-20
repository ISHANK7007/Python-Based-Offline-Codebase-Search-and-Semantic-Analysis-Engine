import ast
from typing import Any, Dict

class ComplexityAnalyzer:
    def analyze(self, node: ast.FunctionDef) -> Dict[str, Any]:
        metrics = {
            "cyclomatic_complexity": 1,
            "branch_count": 0,
            "loop_count": 0,
            "exception_handlers": 0,
            "return_points": 0,
            "max_nesting": 0,
            "is_complex": False,
        }

        def visit(node, nesting=0):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                metrics["cyclomatic_complexity"] += 1
                metrics["branch_count"] += isinstance(node, ast.If)
                metrics["loop_count"] += isinstance(node, (ast.For, ast.While))
                metrics["exception_handlers"] += isinstance(node, ast.Try)
                metrics["max_nesting"] = max(metrics["max_nesting"], nesting + 1)

            if isinstance(node, ast.Return):
                metrics["return_points"] += 1

            for child in ast.iter_child_nodes(node):
                visit(child, nesting + 1)

        visit(node)

        metrics["is_complex"] = (
            metrics["cyclomatic_complexity"] > 3
            or metrics["max_nesting"] > 2
            or metrics["branch_count"] > 1
        )

        return metrics
