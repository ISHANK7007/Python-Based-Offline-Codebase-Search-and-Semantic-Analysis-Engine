from semantic.diff_logic_core import DiffStrategy
from semantic.semantic_diff_engine import ASTBasedDiffStrategy
from semantic.semantic_diff_pluggable import MLSemanticDiffStrategy

class HybridDiffStrategy(DiffStrategy):
    """
    Hybrid diffing strategy combining AST-based structural analysis
    with ML-based semantic understanding.
    """

    def __init__(self, ml_strategy=None, structural_weight=0.6, semantic_weight=0.4):
        """
        Initialize with optional ML strategy and adjustable weights.

        Args:
            ml_strategy: ML-based diffing strategy
            structural_weight: Weight for structural comparison (0-1)
            semantic_weight: Weight for semantic comparison (0-1)
        """
        self.ast_strategy = ASTBasedDiffStrategy()
        self.ml_strategy = ml_strategy or MLSemanticDiffStrategy()
        self.structural_weight = structural_weight
        self.semantic_weight = semantic_weight

        # Normalize weights to ensure they sum to 1
        total = self.structural_weight + self.semantic_weight
        if total == 0:
            raise ValueError("structural_weight and semantic_weight cannot both be zero.")
        self.structural_weight /= total
        self.semantic_weight /= total

    def compare(self, element1, element2, context=None):
        """Compare using both structural and semantic approaches."""
        structural_result = self.ast_strategy.compare(element1, element2, context)
        semantic_result = self.ml_strategy.compare(element1, element2, context)

        # Merge structural and semantic results
        result = structural_result.copy()

        if 'semantic' in semantic_result:
            result['semantic'] = semantic_result['semantic']
            result.setdefault('impact', {})

            # Use semantic prediction to enhance impact assessment
            if 'functionality_changed' in semantic_result['semantic']:
                structural_impact = result['impact'].get('score', 0.5)
                semantic_impact = 1.0 if semantic_result['semantic']['functionality_changed'] else 0.1

                # Blend scores based on weights
                result['impact']['score'] = (
                    self.structural_weight * structural_impact +
                    self.semantic_weight * semantic_impact
                )

                # Flag possibly breaking changes if semantic confidence is high
                if semantic_impact > 0.8 and not result['impact'].get('api_breaking', False):
                    result['impact']['possibly_breaking'] = True

        return result

    def match_symbols(self, symbol, index1, index2, threshold=0.65):
        """Match symbols using both structural and semantic approaches."""
        struct_match, struct_score = self.ast_strategy.match_symbols(symbol, index1, index2)

        if struct_score >= threshold:
            return struct_match, struct_score

        sem_match, sem_score = self.ml_strategy.match_symbols(symbol, index1, index2)

        if sem_score >= threshold:
            return sem_match, sem_score

        if struct_match == sem_match and struct_match is not None:
            combined_score = (
                self.structural_weight * struct_score +
                self.semantic_weight * sem_score
            )
            if combined_score >= threshold:
                return struct_match, combined_score

        if struct_score >= sem_score and struct_score >= 0.4:
            return struct_match, struct_score
        elif sem_score >= 0.4:
            return sem_match, sem_score

        return None, 0.0
