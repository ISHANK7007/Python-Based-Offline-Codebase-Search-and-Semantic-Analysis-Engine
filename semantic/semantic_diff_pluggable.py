from models.semantic_diff_model import SemanticFunctionDiff

class TextDiffFormatter:
    """Format semantic diffs as colored terminal output."""
    
    def __init__(self):
        self.colors = {
            'header': '\033[95m',
            'added': '\033[92m',
            'removed': '\033[91m',
            'modified': '\033[93m',
            'reset': '\033[0m'
        }

    def format_diff(self, diff):
        """Format a SemanticFunctionDiff for terminal output with special handling for missing symbols"""
        lines = []
        c = self.colors  # For brevity

        # Header section with symbol info
        lines.append(f"{c['header']}Function: {diff.symbol}{c['reset']}")
        lines.append(f"{c['header']}Comparing {diff.version1} → {diff.version2}{c['reset']}")

        # Handle special cases for missing symbols
        if diff.availability == SemanticFunctionDiff.AVAILABILITY_ADDED:
            lines.append(f"{c['added']}⭐ NEW FUNCTION: This function was added in {diff.version2}{c['reset']}")

            if diff.metadata_new:
                meta = diff.metadata_new
                lines.append("")
                lines.append(f"{c['header']}Details:{c['reset']}")
                lines.append(f"  Location: {meta['file_path']}:{meta['line_range'][0]}-{meta['line_range'][1]}")

                if meta.get('decorators'):
                    lines.append(f"  Decorators: {', '.join(meta['decorators'])}")

                if meta.get('arguments'):
                    args_str = []
                    for arg in meta['arguments']:
                        arg_str = arg['name']
                        if arg.get('type'):
                            arg_str += f": {arg['type']}"
                        if arg.get('default'):
                            arg_str += f" = {arg['default']}"
                        args_str.append(arg_str)
                    lines.append(f"  Arguments: {', '.join(args_str)}")

                if meta.get('return_annotation'):
                    lines.append(f"  Returns: {meta['return_annotation']}")

                if meta.get('docstring'):
                    lines.append(f"  Documentation: {meta['docstring'].split('.')[0]}...")

                lines.append("")
                lines.append(f"Impact: {c['added']}0.7/1.0 [NEW FUNCTION]{c['reset']}")

            return "\n".join(lines)

        elif diff.availability == SemanticFunctionDiff.AVAILABILITY_REMOVED:
            lines.append(f"{c['removed']}⛔ REMOVED FUNCTION: This function was removed in {diff.version2}{c['reset']}")

            if diff.metadata_old:
                meta = diff.metadata_old
                lines.append("")
                lines.append(f"{c['header']}Details from {diff.version1}:{c['reset']}")
                lines.append(f"  Location: {meta['file_path']}:{meta['line_range'][0]}-{meta['line_range'][1]}")

                if meta.get('decorators'):
                    lines.append(f"  Decorators: {', '.join(meta['decorators'])}")

                if meta.get('arguments'):
                    args_str = []
                    for arg in meta['arguments']:
                        arg_str = arg['name']
                        if arg.get('type'):
                            arg_str += f": {arg['type']}"
                        if arg.get('default'):
                            arg_str += f" = {arg['default']}"
                        args_str.append(arg_str)
                    lines.append(f"  Arguments: {', '.join(args_str)}")

                if meta.get('return_annotation'):
                    lines.append(f"  Returns: {meta['return_annotation']}")

                if meta.get('docstring'):
                    lines.append(f"  Documentation: {meta['docstring'].split('.')[0]}...")

                lines.append("")
                lines.append(f"Impact: {c['removed']}1.0/1.0 [API BREAKING]{c['reset']}")

            return "\n".join(lines)

        elif diff.availability == SemanticFunctionDiff.AVAILABILITY_RENAMED:
            lines.append(f"{c['modified']}🔄 RENAMED FUNCTION: This function appears to have been renamed:{c['reset']}")
            lines.append(f"  {c['removed']}- {diff.symbol} (in {diff.version1}){c['reset']}")
            lines.append(f"  {c['added']}+ {diff.renamed_symbol} (in {diff.version2}){c['reset']}")
            lines.append("")
            lines.append(f"Impact: {c['modified']}0.8/1.0 [POTENTIAL API CHANGE]{c['reset']}")
            lines.append("")
            lines.append(f"Use '--symbol1 {diff.symbol} --symbol2 {diff.renamed_symbol}' for a detailed comparison")

            return "\n".join(lines)

        # Continue with standard diff if function exists in both versions
        lines.append("")
        lines.append(f"{c['header']}Changes:{c['reset']}")

        if diff.signature_changed:
            lines.append(f"{c['modified']}⚠ Signature changed{c['reset']}")
        if diff.body_changed:
            lines.append(f"{c['modified']}📄 Body changed: +{diff.changes['body']['lines_added']} -{diff.changes['body']['lines_removed']}{c['reset']}")
        if diff.doc_changed:
            lines.append(f"{c['modified']}📝 Docstring changed{c['reset']}")

        if diff.impact['api_breaking']:
            lines.append(f"Impact: {c['removed']}1.0/1.0 [API BREAKING]{c['reset']}")
        elif diff.impact['behavior_changing']:
            lines.append(f"Impact: {c['modified']}{diff.impact['score']:.1f}/1.0 [Behavior Changing]{c['reset']}")
        else:
            lines.append(f"Impact: {c['added']}{diff.impact['score']:.1f}/1.0 [Safe]{c['reset']}")

        return "\n".join(lines)
