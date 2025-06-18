from models.semantic_diff_model import SemanticFunctionDiff

class SideBySideMarkdownFormatter:
    """Format semantic diffs as side-by-side Markdown tables for CI integration"""

    def __init__(self, syntax_highlight=True, line_numbers=True):
        self.syntax_highlight = syntax_highlight
        self.line_numbers = line_numbers

    def format_diff(self, diff):
        """Format a SemanticFunctionDiff as a Markdown document with side-by-side tables"""
        lines = []

        # Header
        lines.append(f"# Function Diff: `{diff.symbol}`")
        lines.append(f"Comparing **{diff.version1}** → **{diff.version2}**")

        # Impact summary
        impact_label = "Normal Change"
        if diff.impact.get('api_breaking'):
            impact_label = "⚠️ **API BREAKING**"
        elif diff.impact.get('behavior_changing'):
            impact_label = "⚠️ **BEHAVIOR CHANGING**"

        lines.append(f"**Impact Score**: {diff.impact.get('score', 0):.2f}/1.0 - {impact_label}")
        lines.append("")

        # Handle special availability cases
        if diff.availability != SemanticFunctionDiff.AVAILABILITY_BOTH:
            if diff.availability == SemanticFunctionDiff.AVAILABILITY_ADDED:
                lines.append("## ⭐ NEW FUNCTION")
                lines.append(f"This function was added in {diff.version2}")
                if diff.metadata_new:
                    self._add_function_metadata(lines, diff.metadata_new)
            elif diff.availability == SemanticFunctionDiff.AVAILABILITY_REMOVED:
                lines.append("## ⛔ REMOVED FUNCTION")
                lines.append(f"This function was removed in {diff.version2}")
                if diff.metadata_old:
                    self._add_function_metadata(lines, diff.metadata_old)
            elif diff.availability == SemanticFunctionDiff.AVAILABILITY_RENAMED:
                lines.append("## 🔄 RENAMED FUNCTION")
                lines.append(f"This function appears to have been renamed from `{diff.symbol}` to `{diff.renamed_symbol}`")
            return "\n".join(lines)

        # Decorators diff
        if diff.changes.get('decorators', {}).get('added') or diff.changes.get('decorators', {}).get('removed'):
            lines.append("## Decorators")
            lines.append(f"| {diff.version1} | {diff.version2} |")
            lines.append("| --- | --- |")

            removed = set(diff.changes['decorators'].get('removed', []))
            added = set(diff.changes['decorators'].get('added', []))
            all_decorators = removed.union(added)

            for decorator in all_decorators:
                left = f"~~{decorator}~~" if decorator in removed else ""
                right = f"**{decorator}**" if decorator in added else ""
                lines.append(f"| {left} | {right} |")
            lines.append("")

        # Arguments diff
        args_changes = diff.changes.get('arguments', {})
        if args_changes.get('added') or args_changes.get('removed') or args_changes.get('modified'):
            lines.append("## Arguments")
            lines.append(f"| {diff.version1} | {diff.version2} |")
            lines.append("| --- | --- |")

            removed_args = {a['name']: a for a in args_changes.get('removed', [])}
            added_args = {a['name']: a for a in args_changes.get('added', [])}
            modified_args = args_changes.get('modified', {})

            for name, pair in modified_args.items():
                before = self._format_arg_markdown(pair.get('before'), strikethrough=True)
                after = self._format_arg_markdown(pair.get('after'), strikethrough=False)
                lines.append(f"| {before} | {after} |")

            for name, arg in removed_args.items():
                if name not in modified_args:
                    left = self._format_arg_markdown(arg, strikethrough=True)
                    lines.append(f"| {left} | |")

            for name, arg in added_args.items():
                if name not in modified_args:
                    right = self._format_arg_markdown(arg, strikethrough=False)
                    lines.append(f"| | {right} |")
            lines.append("")

        # Return type diff
        if diff.changes.get('returns', {}).get('type_changed'):
            before_type = diff.changes['returns'].get('before_type', 'None')
            after_type = diff.changes['returns'].get('after_type', 'None')

            lines.append("## Return Type")
            lines.append(f"| {diff.version1} | {diff.version2} |")
            lines.append("| --- | --- |")
            lines.append(f"| ~~`{before_type}`~~ | **`{after_type}`** |")
            lines.append("")

        # Function body diff
        if diff.body_changed and diff.source_diff:
            lines.append("## Function Body")
            changes = diff.changes.get('body', {})
            lines.append(f"**Changes:** +{changes.get('lines_added', 0)} / -{changes.get('lines_removed', 0)} lines")
            if 'complexity_before' in changes and 'complexity_after' in changes:
                lines.append(f"**Complexity:** {changes['complexity_before']} → {changes['complexity_after']}")
            lines.append("")
            self._add_source_diff_markdown(
                lines,
                diff.source_diff,
                diff.version1,
                diff.version2,
                self.syntax_highlight,
                self.line_numbers
            )
            lines.append("")

        # Docstring diff
        if diff.doc_changed:
            before = diff.changes.get('docstring', {}).get('before', '')
            after = diff.changes.get('docstring', {}).get('after', '')
            lines.append("## Documentation")
            lines.append(f"| {diff.version1} | {diff.version2} |")
            lines.append("| --- | --- |")
            lines.append(f"| {before} | {after} |")
            lines.append("")

        return "\n".join(lines)

    def _format_arg_markdown(self, arg, strikethrough=False):
        if not arg:
            return ""
        text = arg.get('name', '')
        if arg.get('type'):
            text += f": `{arg['type']}`"
        if arg.get('default'):
            text += f" = `{arg['default']}`"
        return f"~~{text}~~" if strikethrough else f"**{text}**"

    def _add_function_metadata(self, lines, metadata):
        lines.append("")
        lines.append("### Function Details")
        if 'file_path' in metadata and 'line_range' in metadata:
            lines.append(f"**Location:** `{metadata['file_path']}:{metadata['line_range'][0]}-{metadata['line_range'][1]}`")
        if metadata.get('decorators'):
            lines.append(f"**Decorators:** {', '.join(f'`{d}`' for d in metadata['decorators'])}")
        if metadata.get('arguments'):
            lines.append("**Arguments:**")
            for arg in metadata['arguments']:
                arg_str = f"- `{arg['name']}`"
                if arg.get('type'):
                    arg_str += f": `{arg['type']}`"
                if arg.get('default'):
                    arg_str += f" = `{arg['default']}`"
                lines.append(arg_str)
        if metadata.get('return_annotation'):
            lines.append(f"**Returns:** `{metadata['return_annotation']}`")
        if metadata.get('docstring'):
            lines.append("**Documentation:**")
            lines.append(f"> {metadata['docstring']}")
        lines.append("")

    def _add_source_diff_markdown(self, lines, diff_lines, version1, version2, syntax_highlight=True, line_numbers=True):
        left_lines = []
        right_lines = []

        for diff_type, old_line, new_line, old_num, new_num in diff_lines:
            left_lines.append(f"{old_num}: {old_line}" if old_line and line_numbers else old_line or "")
            right_lines.append(f"{new_num}: {new_line}" if new_line and line_numbers else new_line or "")

        lines.append(f"| {version1} | {version2} |")
        lines.append("| --- | --- |")

        lang = "python" if syntax_highlight else ""
        left_block = f"```{lang}\n" + "\n".join(left_lines) + "\n```"
        right_block = f"```{lang}\n" + "\n".join(right_lines) + "\n```"

        lines.append(f"| {left_block} | {right_block} |")
