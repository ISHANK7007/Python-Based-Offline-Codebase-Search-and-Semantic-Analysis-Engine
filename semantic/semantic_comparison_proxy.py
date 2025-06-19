class TextDiffFormatter:
    """Format semantic diffs for terminal display with ANSI colors"""
    
    def __init__(self, color_enabled=True):
        self.color_enabled = color_enabled  # Allow disabling colors
        # Define color codes
        self.colors = {
            'header': '\033[1;36m',  # Bold Cyan for headers
            'added': '\033[1;32m',    # Bold Green for additions
            'removed': '\033[1;31m',  # Bold Red for removals
            'modified': '\033[1;33m', # Bold Yellow for modifications
            'unchanged': '\033[0;37m',# Light Gray for context
            'reset': '\033[0m'        # Reset to default
        } if color_enabled else {k: '' for k in ['header', 'added', 'removed', 'modified', 'unchanged', 'reset']}
    
    def format_diff(self, diff):
        """Format a SemanticFunctionDiff for terminal output"""
        lines = []
        c = self.colors  # For brevity
        
        # Header section with symbol and summary
        lines.append(f"{c['header']}Function: {diff.symbol}{c['reset']}")
        lines.append(f"{c['header']}Comparing {diff.version1} → {diff.version2}{c['reset']}")
        
        # Impact summary
        impact_color = c['unchanged']
        if diff.impact['api_breaking']:
            impact_color = c['removed']
        elif diff.impact['behavior_changing']:
            impact_color = c['modified']
        
        lines.append(f"Impact: {impact_color}{diff.impact['score']:.2f}/1.0{c['reset']}" + 
                    (f" {c['removed']}[API BREAKING]{c['reset']}" if diff.impact['api_breaking'] else ""))
        
        lines.append("")  # Empty line for readability
        
        # Decorator changes
        if diff.changes['decorators']['added'] or diff.changes['decorators']['removed']:
            lines.append(f"{c['header']}Decorators:{c['reset']}")
            for decorator in diff.changes['decorators']['added']:
                lines.append(f"  {c['added']}+ {decorator}{c['reset']}")
            for decorator in diff.changes['decorators']['removed']:
                lines.append(f"  {c['removed']}- {decorator}{c['reset']}")
            lines.append("")
        
        # Argument changes
        if diff.changes['arguments']['added'] or diff.changes['arguments']['removed'] or diff.changes['arguments']['modified']:
            lines.append(f"{c['header']}Arguments:{c['reset']}")
            for arg in diff.changes['arguments']['added']:
                lines.append(f"  {c['added']}+ {arg['name']}: {arg.get('type', 'Any')}" + 
                           (f" = {arg['default']}" if 'default' in arg else "") + f"{c['reset']}")
            for arg in diff.changes['arguments']['removed']:
                lines.append(f"  {c['removed']}- {arg['name']}: {arg.get('type', 'Any')}" + 
                           (f" = {arg['default']}" if 'default' in arg else "") + f"{c['reset']}")
            for arg in diff.changes['arguments']['modified']:
                lines.append(f"  {c['modified']}~ {arg['name']}:{c['reset']}")
                if arg.get('type_before') != arg.get('type_after'):
                    lines.append(f"    {c['removed']}- type: {arg.get('type_before', 'Any')}{c['reset']}")
                    lines.append(f"    {c['added']}+ type: {arg.get('type_after', 'Any')}{c['reset']}")
                if arg.get('default_before') != arg.get('default_after'):
                    lines.append(f"    {c['removed']}- default: {arg.get('default_before', 'None')}{c['reset']}")
                    lines.append(f"    {c['added']}+ default: {arg.get('default_after', 'None')}{c['reset']}")
            lines.append("")
        
        # Return type changes
        if diff.changes['returns']['type_changed']:
            lines.append(f"{c['header']}Return Type:{c['reset']}")
            lines.append(f"  {c['removed']}- {diff.changes['returns']['before_type'] or 'None'}{c['reset']}")
            lines.append(f"  {c['added']}+ {diff.changes['returns']['after_type'] or 'None'}{c['reset']}")
            lines.append("")
        
        # Function body summary
        if diff.body_changed:
            lines.append(f"{c['header']}Function Body:{c['reset']}")
            lines.append(f"  {c['added']}+ {diff.changes['body']['lines_added']} lines added{c['reset']}")
            lines.append(f"  {c['removed']}- {diff.changes['body']['lines_removed']} lines removed{c['reset']}")
            if 'complexity_before' in diff.changes['body'] and 'complexity_after' in diff.changes['body']:
                complexity_color = c['unchanged']
                if diff.changes['body']['complexity_after'] > diff.changes['body']['complexity_before']:
                    complexity_color = c['modified']
                lines.append(f"  Complexity: {complexity_color}{diff.changes['body']['complexity_before']} → " + 
                           f"{diff.changes['body']['complexity_after']}{c['reset']}")
            lines.append("")
        
        # Docstring changes
        if diff.doc_changed:
            lines.append(f"{c['header']}Documentation:{c['reset']}")
            if diff.changes['docstring'].get('params_changed'):
                lines.append(f"  {c['modified']}Parameter documentation updated{c['reset']}")
            if diff.changes['docstring'].get('before') and diff.changes['docstring'].get('after'):
                # Show condensed diff for docstrings
                lines.append(f"  {c['modified']}Docstring text updated{c['reset']}")
            lines.append("")
        
        return "\n".join(lines)