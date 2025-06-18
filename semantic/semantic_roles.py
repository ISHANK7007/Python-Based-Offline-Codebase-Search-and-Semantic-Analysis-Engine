
def extract_function_calls(self, element):
    """Extract function calls from the element's code."""
    if element.type != "function":
        return []
    
    # Lazily initialize the call resolver
    if not hasattr(self, 'call_resolver'):
        from semantic.resolver import CallTargetResolver  # Local import to avoid circular dependency
        self.call_resolver = CallTargetResolver(index=self.index if hasattr(self, 'index') else None)
    
    # Resolve calls using the resolver
    resolved_calls = self.call_resolver.resolve_calls_in_function(element)
    
    # Filter and return valid resolved call targets
    return [
        target for target in resolved_calls.values()
        if isinstance(target, dict) and target.get('type') != 'unresolved'
    ]
