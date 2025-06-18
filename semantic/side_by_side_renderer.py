import os
from shutil import get_terminal_size

from semantic.diff_output_formatter import TextDiffFormatter
from models.semantic_diff_model import SemanticFunctionDiff





class SideBySideTerminalFormatter:
    """Format semantic diffs as side-by-side terminal output with ANSI colors"""
    
    def __init__(self, color_enabled=True, width=None, syntax_highlight=True, line_numbers=True):
        self.color_enabled = color_enabled
        self.syntax_highlight = syntax_highlight
        self.line_numbers = line_numbers
        
        if width is None:
            terminal_width, _ = get_terminal_size()
            self.width = terminal_width
        else:
            self.width = width
        
        self.colors = {
            'header': '\033[1;36m',
            'added': '\033[1;32m',
            'removed': '\033[1;31m',
            'modified': '\033[1;33m',
            'unchanged': '\033[0;37m',
            'reset': '\033[0m'
        } if color_enabled else {k: '' for k in ['header', 'added', 'removed', 'modified', 'unchanged', 'reset']}
        
        self.column_width = max(30, int(self.width * 0.45))
    
    def format_diff(self, diff):
        if diff.availability != SemanticFunctionDiff.AVAILABILITY_BOTH:
            return TextDiffFormatter(self.color_enabled).format_diff(diff)
        
        lines = []
        c = self.colors
        
        header = f"{c['header']}Function: {diff.symbol} ({diff.version1} → {diff.version2}){c['reset']}"
        lines.append(header)
        
        impact_color = c['unchanged']
        if diff.impact.get('api_breaking'):
            impact_color = c['removed']
        elif diff.impact.get('behavior_changing'):
            impact_color = c['modified']
        
        impact_line = f"Impact: {impact_color}{diff.impact.get('score', 0.0):.2f}/1.0{c['reset']}"
        if diff.impact.get('api_breaking'):
            impact_line += f" {c['removed']}[API BREAKING]{c['reset']}"
        lines.append(impact_line)
        lines.append("")
        
        left_header = f"{diff.version1}".ljust(self.column_width)
        right_header = f"{diff.version2}"
        lines.append(f"{c['header']}{left_header} | {right_header}{c['reset']}")
        lines.append("-" * self.column_width + "+" + "-" * self.column_width)

        # Decorators
        if diff.changes.get('decorators', {}).get('added') or diff.changes.get('decorators', {}).get('removed'):
            lines.append(f"{c['header']}Decorators:{c['reset']}")
            left_decorators = set(diff.changes['decorators'].get('removed', []))
            right_decorators = set(diff.changes['decorators'].get('added', []))
            all_decorators = left_decorators | right_decorators

            for decorator in all_decorators:
                left_str = f"{c['removed']}{decorator}{c['reset']}" if decorator in left_decorators else " " * len(decorator)
                right_str = f"{c['added']}{decorator}{c['reset']}" if decorator in right_decorators else ""
                lines.append(f"{left_str.ljust(self.column_width)} | {right_str}")
            lines.append("-" * self.column_width + "+" + "-" * self.column_width)

        # Arguments
        if any(diff.changes.get('arguments', {}).get(k) for k in ['added', 'removed', 'modified']):
            lines.append(f"{c['header']}Arguments:{c['reset']}")
            left_args = {arg['name']: arg for arg in diff.changes['arguments'].get('removed', [])}
            right_args = {arg['name']: arg for arg in diff.changes['arguments'].get('added', [])}
            modified_args = {arg['name']: arg for arg in diff.changes['arguments'].get('modified', [])}

            for name, arg_changes in modified_args.items():
                left_arg = arg_changes.get('before', {})
                right_arg = arg_changes.get('after', {})
                left_str = self._format_argument(left_arg, c['removed'])
                right_str = self._format_argument(right_arg, c['added'])
                lines.append(f"{left_str.ljust(self.column_width)} | {right_str}")
            
            for name, arg in left_args.items():
                if name not in modified_args:
                    left_str = self._format_argument(arg, c['removed'])
                    lines.append(f"{left_str.ljust(self.column_width)} | ")
            
            for name, arg in right_args.items():
                if name not in modified_args:
                    right_str = self._format_argument(arg, c['added'])
                    lines.append(f"{' '.ljust(self.column_width)} | {right_str}")
            
            lines.append("-" * self.column_width + "+" + "-" * self.column_width)

        # Return Type
        if diff.changes.get('returns', {}).get('type_changed'):
            lines.append(f"{c['header']}Return Type:{c['reset']}")
            left_type = diff.changes['returns'].get('before_type', 'None')
            right_type = diff.changes['returns'].get('after_type', 'None')
            left_str = f"{c['removed']}{left_type}{c['reset']}"
            right_str = f"{c['added']}{right_type}{c['reset']}"
            lines.append(f"{left_str.ljust(self.column_width)} | {right_str}")
            lines.append("-" * self.column_width + "+" + "-" * self.column_width)

        # Function Body
        if diff.body_changed and diff.source_diff:
            lines.append(f"{c['header']}Function Body:{c['reset']}")
            lines.extend(self._format_source_diff(
                diff.source_diff,
                self.column_width,
                self.syntax_highlight,
                self.line_numbers
            ))
            lines.append("-" * self.column_width + "+" + "-" * self.column_width)

        return "\n".join(lines)

    def _format_argument(self, arg, color_code):
        if not arg:
            return ""
        arg_str = arg.get('name', '')
        if arg.get('type'):
            arg_str += f": {arg['type']}"
        if arg.get('default'):
            arg_str += f" = {arg['default']}"
        return f"{color_code}{arg_str}{self.colors['reset']}"

    def _format_source_diff(self, diff_lines, width, highlight=True, show_line_numbers=True):
        result = []
        for diff_type, old_line, new_line, old_num, new_num in diff_lines:
            old_num_str = f"{old_num:4d}| " if old_num and show_line_numbers else "     "
            new_num_str = f"{new_num:4d}| " if new_num and show_line_numbers else "     "
            display_width = width - (6 if show_line_numbers else 0)

            old_display = (old_line or "")[:display_width]
            new_display = (new_line or "")[:display_width]

            if old_line and len(old_line) > display_width:
                old_display = old_display[:-3] + "..."
            if new_line and len(new_line) > display_width:
                new_display = new_display[:-3] + "..."

            if diff_type == 'removed':
                old_display = f"{self.colors['removed']}{old_display}{self.colors['reset']}"
            elif diff_type == 'added':
                new_display = f"{self.colors['added']}{new_display}{self.colors['reset']}"
            elif diff_type == 'changed':
                old_display = f"{self.colors['removed']}{old_display}{self.colors['reset']}"
                new_display = f"{self.colors['added']}{new_display}{self.colors['reset']}"

            left = f"{old_num_str}{old_display}".ljust(width)
            right = f"{new_num_str}{new_display}"
            result.append(f"{left} | {right}")
        return result
