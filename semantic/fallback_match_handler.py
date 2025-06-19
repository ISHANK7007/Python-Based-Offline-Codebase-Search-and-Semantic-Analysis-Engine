class MarkdownDiffFormatter:
    """Format semantic diffs as markdown for documentation"""
    
    def format_diff(self, diff):
        """Format a SemanticFunctionDiff as markdown"""
        lines = []
        
        # Header with metadata
        lines.append(f"# Function Diff: `{diff.symbol}`")
        lines.append(f"Comparing **{diff.version1}** → **{diff.version2}**\n")
        
        # Impact summary
        impact_label = "Normal Change"
        if diff.impact['api_breaking']:
            impact_label = "⚠️ **API BREAKING**"
        elif diff.impact['behavior_changing']:
            impact_label = "⚠️ **BEHAVIOR CHANGING**"
        
        lines.append(f"**Impact Score**: {diff.impact['score']:.2f}/1.0 - {impact_label}\n")
        
        # Change summary table
        lines.append("## Change Summary")
        lines.append("| Component | Changed | Details |")
        lines.append("| --- | --- | --- |")
        lines.append(f"| Signature | {'✅' if diff.signature_changed else '❌'} | " + 
                   f"{len(diff.changes['arguments']['added']) + len(diff.changes['arguments']['removed']) + len(diff.changes['arguments']['modified'])} argument changes |")
        lines.append(f"| Decorators | {'✅' if diff.changes['decorators']['added'] or diff.changes['decorators']['removed'] else '❌'} | " + 
                   f"{len(diff.changes['decorators']['added'])} added, {len(diff.changes['decorators']['removed'])} removed |")
        lines.append(f"| Return Type | {'✅' if diff.changes['returns']['type_changed'] else '❌'} | " +
                   (f"'{diff.changes['returns']['before_type']}' → '{diff.changes['returns']['after_type']}'" if diff.changes['returns']['type_changed'] else "No change"))
        lines.append(f"| Function Body | {'✅' if diff.body_changed else '❌'} | " +
                   (f"{diff.changes['body']['lines_added']} lines added, {diff.changes['body']['lines_removed']} lines removed" if diff.body_changed else "No change"))
        lines.append(f"| Documentation | {'✅' if diff.doc_changed else '❌'} | " +
                   ("Parameters or description changed" if diff.doc_changed else "No change"))
        
        # Detailed sections for each component...
        # (Detailed markdown sections with code blocks and tables for each component)
        
        return "\n".join(lines)