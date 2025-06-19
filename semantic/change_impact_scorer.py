import json
import yaml

class JsonDiffFormatter:
    """Format semantic diffs as JSON"""
    
    def format_diff(self, diff):
        """Convert SemanticFunctionDiff to JSON"""
        return json.dumps(diff.to_dict(), indent=2)


class YamlDiffFormatter:
    """Format semantic diffs as YAML"""
    
    def format_diff(self, diff):
        """Convert SemanticFunctionDiff to YAML"""
        return yaml.dump(diff.to_dict(), sort_keys=False)
