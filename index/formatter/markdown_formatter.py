class MarkdownComparisonFormatter:
    """Format comparison results in markdown"""
    
    def format_comparison(self, comparison):
        md = f"# Comparison for {comparison['symbol']}\n\n"
        
        if 'decorators' in comparison:
            md += "## Decorators\n"
            md += "* **Added:** " + ", ".join(comparison['decorators']['added']) + "\n"
            md += "* **Removed:** " + ", ".join(comparison['decorators']['removed']) + "\n\n"
        
        # Format other attributes similarly
        
        return md