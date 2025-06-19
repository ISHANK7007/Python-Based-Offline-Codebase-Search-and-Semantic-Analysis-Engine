import os
from index.codebase_index import CodebaseIndex
from semantic.semantic_diff_engine import VersionManager, SemanticFunctionDiff
from cli.commands.compare_output import get_diff_formatter


class CompareExecutor:
    def __init__(self):
        self.version_manager = VersionManager()

    def compare_elements(self, symbol, src1, src2, attributes=None, fuzzy_match=False, threshold=0.7):
        index1 = CodebaseIndex(src1)
        index2 = CodebaseIndex(src2)

        element1 = index1.get_element_by_symbol(symbol)
        element2 = index2.get_element_by_symbol(symbol)

        if not element1 or not element2:
            return {'error': f"Symbol {symbol} not found in one or both sources"}

        # Example: comparing decorators and arguments
        comparison = {}
        if 'decorators' in attributes:
            comparison['decorators'] = {
                'added': [d for d in element2.decorators if d not in element1.decorators],
                'removed': [d for d in element1.decorators if d not in element2.decorators]
            }

        if 'arguments' in attributes:
            comparison['arguments'] = {
                'added': [a for a in element2.arguments if a not in element1.arguments],
                'removed': [a for a in element1.arguments if a not in element2.arguments],
                'modified': []
            }

        return comparison

    def compare_and_render(self, symbol, src1, src2, args):
        diff = self.version_manager.compare_symbols(
            symbol,
            src1,
            src2,
            fuzzy_match=args.fuzzy_match if hasattr(args, 'fuzzy_match') else False
        )

        formatter = get_diff_formatter(
            args.format,
            color_enabled=not getattr(args, 'no_color', False),
            syntax_highlight=getattr(args, 'syntax_highlight', True),
            line_numbers=getattr(args, 'line_numbers', True),
            width=getattr(args, 'width', 100),
            display_mode=getattr(args, 'diff', 'unified')
        )

        output = formatter.format_diff(diff)

        if hasattr(args, 'output_file') and args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(output)
        else:
            print(output)

        if diff.availability == SemanticFunctionDiff.AVAILABILITY_REMOVED:
            return 2 if getattr(args, 'strict', False) else 0
        elif diff.impact.get('api_breaking', False):
            return 1 if getattr(args, 'strict', False) else 0
        return 0