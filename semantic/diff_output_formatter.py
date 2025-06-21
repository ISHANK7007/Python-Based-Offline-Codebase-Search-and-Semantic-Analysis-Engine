from index.formatter.default_formatter import TextDiffFormatter
from index.formatter.markdown_formatter import MarkdownDiffFormatter
from index.formatter.default_formatter import JsonDiffFormatter, YamlDiffFormatter  # 👈 FIXED import

def get_diff_formatter(format_name, **options):
    """Factory function to get the appropriate formatter"""
    formatters = {
        'text': TextDiffFormatter,
        'json': JsonDiffFormatter,
        'yaml': YamlDiffFormatter,
        'markdown': MarkdownDiffFormatter
    }

    if format_name not in formatters:
        raise ValueError(f"Unsupported format: {format_name}")
    
    return formatters[format_name](**options)
