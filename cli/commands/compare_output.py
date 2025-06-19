import os
import re
import json
from abc import ABC, abstractmethod

from models.semantic_diff_model import SemanticFunctionDiff
from index.formatter.markdown_formatter import MarkdownDiffFormatter
from semantic.side_by_side_renderer import SideBySideTerminalFormatter

from index.formatter.default_formatter import DefaultFormatter
from cli.commands.base import Command
from semantic.diff_strategy_registry import DiffStrategyRegistry
from semantic.diff_logic_core import ASTBasedDiffStrategy



def get_diff_formatter(format_type: str,
                       display_mode: str = "unified",
                       color_enabled: bool = True,
                       syntax_highlight: bool = True,
                       line_numbers: bool = True,
                       width: int = 100):
    """Return the appropriate formatter instance based on CLI args."""
    if format_type == 'markdown':
        return MarkdownDiffFormatter(
            display_mode=display_mode,
            syntax_highlight=syntax_highlight,
            line_numbers=line_numbers
        )
    elif format_type == 'text' and display_mode == 'side-by-side':
        return SideBySideTerminalFormatter(
            color_enabled=color_enabled,
            width=width,
            syntax_highlight=syntax_highlight,
            line_numbers=line_numbers
        )
    else:
        return DefaultFormatter(format_type=format_type,
                                syntax_highlight=syntax_highlight,
                                line_numbers=line_numbers,
                                color=color_enabled)


def assert_terminal_output_matches(output: str, expected: str):
    """Assert equality of terminal output while stripping ANSI codes and tolerating whitespace."""
    clean_output = re.sub(r'\033\[[0-9;]+m', '', output)
    clean_expected = re.sub(r'\033\[[0-9;]+m', '', expected)

    output_lines = [line.rstrip() for line in clean_output.splitlines()]
    expected_lines = [line.rstrip() for line in clean_expected.splitlines()]

    assert output_lines == expected_lines, "Visual diff output does not match expected."


class DiffStrategy(ABC):
    """Abstract base class for diffing strategies."""

    @abstractmethod
    def compare(self, element1, element2, context=None):
        pass

    @abstractmethod
    def match_symbols(self, symbol, index1, index2, threshold=0.7):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def description(self):
        return self.__doc__ or "No description available"


class MLSemanticDiffStrategy(DiffStrategy):
    """ML-based semantic diffing using embeddings and semantic similarity."""

    def __init__(self, model_path=None):
        self.model_path = model_path
        self.model = self._load_model(model_path) if model_path else None

    def compare(self, element1, element2, context=None):
        base_result = ASTBasedDiffStrategy().compare(element1, element2, context)

        if element1 and element2:
            embedding1 = self._get_code_embedding(element1)
            embedding2 = self._get_code_embedding(element2)

            semantic_similarity = self._calculate_embedding_similarity(embedding1, embedding2)

            base_result['semantic'] = {
                'similarity_score': semantic_similarity,
                'semantic_equivalent': semantic_similarity > 0.9,
                'functionality_changed': semantic_similarity < 0.7
            }

            if base_result['body'].get('changed', False):
                base_result['body']['semantic_change_magnitude'] = 1.0 - semantic_similarity

        return base_result

    def match_symbols(self, symbol, index1, index2, threshold=0.6):
        source_element = index1.get_element_by_symbol(symbol)
        if not source_element:
            return None, 0.0

        source_embedding = self._get_code_embedding(source_element)

        candidates = []
        for target_symbol in index2.get_all_symbols():
            target_element = index2.get_element_by_symbol(target_symbol)
            target_embedding = self._get_code_embedding(target_element)
            similarity = self._calculate_embedding_similarity(source_embedding, target_embedding)
            candidates.append((target_symbol, similarity))

        candidates.sort(key=lambda x: x[1], reverse=True)
        if candidates and candidates[0][1] >= threshold:
            return candidates[0]

        return None, 0.0

    def _load_model(self, model_path):
        try:
            import torch
            return torch.load(model_path)
        except Exception as e:
            print(f"Warning: Failed to load ML model: {e}")
            return None

    def _get_code_embedding(self, element):
        if not self.model:
            return self._get_default_embedding(element)

        code_str = element.get_source()
        import numpy as np
        return np.random.random(768)

    def _calculate_embedding_similarity(self, embedding1, embedding2):
        import numpy as np
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        return dot_product / (norm1 * norm2)


class ListStrategiesCommand(Command):
    """List available diffing strategies"""

    def configure_parser(self, parser):
        parser.add_argument('--format', choices=['text', 'json'],
                            default='text', help='Output format')

    def run(self, args):
        strategies = DiffStrategyRegistry.list_strategies()

        if args.format == 'json':
            print(json.dumps(strategies, indent=2))
            return 0

        print("Available diffing strategies:")
        print("-----------------------------")
        for strategy in strategies:
            print(f"\n{strategy['name']}:")
            print(f"  {strategy['description']}")
        return 0
