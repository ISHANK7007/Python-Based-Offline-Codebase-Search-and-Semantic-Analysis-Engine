# File: cli/commands/version_manager.py

import os
from semantic.semantic_diff_engine import SemanticDiffEngine
from index.codebase_index import CodebaseIndex

class VersionManager:
    """
    Manages comparison between different versions of a symbol.
    """

    def __init__(self):
        self.diff_engine = SemanticDiffEngine()

    def compare_symbols(self, symbol: str, version1_path: str, version2_path: str, fuzzy_match=False):
        """
        Compare a function symbol across two codebase versions.

        Args:
            symbol (str): The fully qualified name of the function to compare.
            version1_path (str): Path to version 1 of the codebase.
            version2_path (str): Path to version 2 of the codebase.
            fuzzy_match (bool): Whether to allow fuzzy matching for renamed functions.

        Returns:
            SemanticFunctionDiff: The semantic difference object.
        """
        # Index both versions
        index_v1 = CodebaseIndex()
        index_v1.index_directory(version1_path)

        index_v2 = CodebaseIndex()
        index_v2.index_directory(version2_path)

        # Run semantic diff
        diff = self.diff_engine.compare_functions(
            symbol=symbol,
            index_old=index_v1,
            index_new=index_v2,
            fuzzy_match=fuzzy_match
        )

        return diff
