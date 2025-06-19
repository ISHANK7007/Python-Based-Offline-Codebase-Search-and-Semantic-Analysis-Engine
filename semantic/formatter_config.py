import os
from index.codebase_index import CodebaseIndex
from semantic.diff_logic_core import SemanticFunctionDiff
from semantic.diff_strategy_registry import DiffStrategyRegistry

class VersionManager:
    """Manages multiple codebase versions for efficient diffing."""

    def __init__(self, cache_dir=None, diff_strategy=None):
        """Initialize with optional cache directory and diff strategy."""
        self.cache_dir = cache_dir or os.path.expanduser("~/.semantic_indexer/cache")

        # Use default strategy if none specified
        if diff_strategy is None:
            self.diff_strategy = DiffStrategyRegistry.get_strategy("ASTBasedDiffStrategy")
        elif isinstance(diff_strategy, str):
            self.diff_strategy = DiffStrategyRegistry.get_strategy(diff_strategy)
        else:
            self.diff_strategy = diff_strategy

        self.indices = {}  # Map of version_id -> CodebaseIndex

    def get_index(self, path):
        """Return a CodebaseIndex for the given path, using cache if available."""
        if path not in self.indices:
            self.indices[path] = CodebaseIndex(path)
        return self.indices[path]

    def compare_symbols(self, symbol, src1_path, src2_path, fuzzy_match=False, **kwargs):
        """Compare a symbol across two codebases using the configured diff strategy."""
        # Get indices for both versions
        index1 = self.get_index(src1_path)
        index2 = self.get_index(src2_path)

        # Get elements directly if symbol exists in both
        element1 = index1.get_element_by_symbol(symbol)
        element2 = index2.get_element_by_symbol(symbol)

        matched_symbol = None

        # Try fuzzy matching if requested and symbol doesn't exist in both
        if fuzzy_match and ((element1 and not element2) or (not element1 and element2)):
            if element1:
                matched_symbol, score = self.diff_strategy.match_symbols(symbol, index1, index2, **kwargs)
                if matched_symbol:
                    element2 = index2.get_element_by_symbol(matched_symbol)
            else:
                matched_symbol, score = self.diff_strategy.match_symbols(symbol, index2, index1, **kwargs)
                if matched_symbol:
                    element1 = index1.get_element_by_symbol(matched_symbol)

        # Create a SemanticFunctionDiff
        diff = SemanticFunctionDiff(
            symbol=symbol,
            version1=os.path.basename(src1_path),
            version2=os.path.basename(src2_path)
        )

        # Set renamed symbol if found
        if matched_symbol:
            diff.renamed_symbol = matched_symbol
            diff.availability = SemanticFunctionDiff.AVAILABILITY_RENAMED

        # Use strategy to compare elements
        comparison_context = {
            'index1': index1,
            'index2': index2,
            'fuzzy_match': fuzzy_match,
            'src1_path': src1_path,
            'src2_path': src2_path
        }

        comparison_result = self.diff_strategy.compare(element1, element2, comparison_context)

        # Apply comparison results to diff object
        self._populate_diff_from_result(diff, comparison_result, element1, element2)

        return diff

    def _populate_diff_from_result(self, diff, result, element1, element2):
        """Populate the SemanticFunctionDiff object from comparison result."""
        diff.impact = result.get('impact', {})
        diff.changes = result.get('changes', {})
        diff.body_changed = result.get('body_changed', False)
        diff.source_diff = result.get('source_diff', [])
        if element1 and element2:
            diff.availability = SemanticFunctionDiff.AVAILABILITY_BOTH
        elif element1:
            diff.availability = SemanticFunctionDiff.AVAILABILITY_ONLY_SRC1
        elif element2:
            diff.availability = SemanticFunctionDiff.AVAILABILITY_ONLY_SRC2
        else:
            diff.availability = SemanticFunctionDiff.AVAILABILITY_NONE

    def set_diff_strategy(self, strategy):
        """Change the diff strategy at runtime."""
        if isinstance(strategy, str):
            self.diff_strategy = DiffStrategyRegistry.get_strategy(strategy)
        else:
            self.diff_strategy = strategy
