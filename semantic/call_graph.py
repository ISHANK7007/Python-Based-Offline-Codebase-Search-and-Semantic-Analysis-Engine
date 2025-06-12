import ast
from typing import Dict, List, Set, Any, Optional, Tuple, Type

class SemanticVisitorManager:
    """
    Manager class that handles parsing and dispatching to multiple visitors.
    This avoids redundant parsing while allowing specialized visitors.
    """
    def __init__(self, indexer):
        self.indexer = indexer
        self.visitors = {}  # Visitor name -> visitor instance
        
    def register_visitor(self, name, visitor_class, **kwargs):
        """Register a new visitor by name with optional init params."""
        self.visitors[name] = visitor_class(self.indexer, **kwargs)
        
    def analyze_element(self, element, visitor_names=None):
        """
        Analyze an element with all registered visitors, or a subset if names provided.
        Returns a dictionary of results keyed by visitor name.
        """
        if not hasattr(element, 'ast_node'):
            # Parse the AST only once
            try:
                if element.type == 'function':
                    code_text = element.body
                    element.ast_node = ast.parse(code_text).body[0]
                elif element.type == 'class':
                    code_text = element.definition
                    element.ast_node = ast.parse(code_text).body[0]
                elif element.type == 'module':
                    code_text = element.source
                    element.ast_node = ast.parse(code_text)
                else:
                    # Can't parse this element type
                    return {}
            except SyntaxError:
                # Handle syntax errors gracefully
                return {'error': 'Syntax error in parsing'}
        
        # Determine which visitors to use
        active_visitors = self.visitors
        if visitor_names:
            active_visitors = {name: self.visitors[name] 
                              for name in visitor_names 
                              if name in self.visitors}
        
        # Run each visitor and collect results
        results = {}
        for name, visitor in active_visitors.items():
            results[name] = visitor.analyze(element)
        
        return results