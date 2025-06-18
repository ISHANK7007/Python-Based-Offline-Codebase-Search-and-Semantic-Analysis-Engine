
class FunctionFingerprintHelper:
    """Provides fingerprinting and rename detection for functions."""

    def _generate_function_fingerprint(self, func_node):
        """Generate a fingerprint that's resilient to variable renaming and formatting changes"""
        # 1. Normalize the AST (replace variable names, remove comments, normalize whitespace)
        normalized_ast = self._normalize_ast(func_node.ast_node)

        # 2. Extract key structural components that survive renaming
        components = {
            'arg_count': len(func_node.arguments),
            'arg_types': [arg.get('type_annotation') for arg in func_node.arguments],
            'return_type': func_node.return_annotation,
            'decorator_count': len(func_node.decorators),
            'calls_count': len(func_node.calls),
            # Generate stable hash of normalized code structure that ignores names
            'body_hash': self._hash_normalized_body(normalized_ast.body)
        }

        return components

    def _find_possible_rename(self, symbol, index1, index2):
        """Try to find a renamed version of the symbol in the other codebase"""
        # Determine which index has the element
        source_index = index1 if index1.has_symbol(symbol) else index2
        target_index = index2 if source_index == index1 else index1

        if not source_index.has_symbol(symbol):
            return None

        # Get the source element
        source_element = source_index.get_element_by_symbol(symbol)

        # Generate signature fingerprint
        fingerprint = self._generate_function_fingerprint(source_element)

        # Get candidate functions in target codebase
        # First, try functions with similar names
        name_parts = symbol.split('.')
        simple_name = name_parts[-1]
        module_prefix = '.'.join(name_parts[:-1]) if len(name_parts) > 1 else ""

        candidates = []

        # Try similar module paths first
        if module_prefix:
            similar_modules = target_index.find_symbols_by_prefix(module_prefix)
            for candidate in similar_modules:
                if candidate.split('.')[-1] == simple_name:
                    candidates.append((candidate, 0.9))  # High confidence for same name in similar module

        # Try functions with similar names in any module
        similar_names = target_index.find_symbols_by_name(simple_name)
        for candidate in similar_names:
            if candidate not in [c[0] for c in candidates]:
                candidates.append((candidate, 0.6))  # Medium confidence for same name anywhere

        # Sort candidates by fingerprint similarity
        scored_candidates = []
        for candidate_symbol, base_score in candidates:
            candidate_element = target_index.get_element_by_symbol(candidate_symbol)
            if not candidate_element:
                continue

            candidate_fingerprint = self._generate_function_fingerprint(candidate_element)
            similarity = self._calculate_fingerprint_similarity(fingerprint, candidate_fingerprint)

            # Final score combines name-based score and fingerprint similarity
            final_score = base_score * 0.3 + similarity * 0.7
            scored_candidates.append((candidate_symbol, final_score))

        # Return best match if it's above threshold
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        if scored_candidates and scored_candidates[0][1] >= 0.7:  # Configurable threshold
            return scored_candidates[0][0]

        return None
