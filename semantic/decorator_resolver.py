class DecoratorResolver:
    """Resolves and categorizes decorators during semantic indexing"""
    
    def __init__(self):
        # Known decorator mappings
        self.known_decorators = {
            'route': {'category': 'routing', 'framework': 'flask'},
            'login_required': {'category': 'auth', 'framework': 'flask'},
            'admin_required': {'category': 'auth', 'framework': 'custom'},
            'api': {'category': 'api', 'framework': 'fastapi'},
            'cached': {'category': 'caching', 'framework': 'generic'},
            # Additional mappings...
        }
    
    def resolve_decorator(self, decorator_expr):
        """
        Analyze a decorator expression and return semantic information
        Even if it can't be fully resolved, capture what we know
        """
        # Extract the base name without arguments
        base_name = self._extract_base_name(decorator_expr)
        
        # Look up in known decorators
        if base_name in self.known_decorators:
            result = self.known_decorators[base_name].copy()
            result['name'] = base_name
            result['resolved'] = True
            result['original'] = decorator_expr
            return result
        
        # For unknown/unresolved decorators, capture what we can
        return {
            'name': base_name,
            'original': decorator_expr,
            'resolved': False,
            'category': 'unknown',
            'partial_info': self._extract_partial_info(decorator_expr)
        }
    
    def _extract_base_name(self, decorator_expr):
        """Extract base decorator name from potentially complex expression"""
        # Handle simple case: @decorator_name
        if '(' not in decorator_expr:
            return decorator_expr.lstrip('@')
        
        # Handle case with arguments: @decorator_name(args)
        return decorator_expr.split('(')[0].lstrip('@')
    
    def _extract_partial_info(self, decorator_expr):
        """Extract partial information from unresolved decorators"""
        # Look for hints in the name
        base_name = self._extract_base_name(decorator_expr)
        
        partial_info = {}
        
        # Check for common patterns in naming
        if 'auth' in base_name or 'login' in base_name or 'permission' in base_name:
            partial_info['likely_category'] = 'auth'
        elif 'route' in base_name or 'url' in base_name or 'path' in base_name:
            partial_info['likely_category'] = 'routing'
        elif 'cache' in base_name or 'memoize' in base_name:
            partial_info['likely_category'] = 'caching'
        elif 'api' in base_name or 'rest' in base_name or 'endpoint' in base_name:
            partial_info['likely_category'] = 'api'
        
        # Check for arguments that might give hints
        if '(' in decorator_expr:
            args_str = decorator_expr.split('(', 1)[1].rsplit(')', 1)[0]
            partial_info['args_excerpt'] = args_str[:50] + ('...' if len(args_str) > 50 else '')
        
        return partial_info