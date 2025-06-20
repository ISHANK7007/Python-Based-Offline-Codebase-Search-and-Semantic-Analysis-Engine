class ExecutionPlan:
    """Represents optimized execution plan for a filter query"""
    
    def __init__(self, indexed_lookups=None, prefix_lookups=None, remaining_filters=None):
        self.indexed_lookups = indexed_lookups or []
        self.prefix_lookups = prefix_lookups or []
        self.remaining_filters = remaining_filters or []
        
    def execute(self, index):
        """Execute the plan against the index"""
        # Start with full candidate set
        candidates = set(index._elements.values())

        
        # Apply indexed lookups (exact match on indexed fields)
        for lookup in self.indexed_lookups:
            field_index = self._get_index_for_field(index, lookup.field_name)
            if field_index and lookup.value in field_index:
                lookup_results = set(field_index[lookup.value])
                candidates &= lookup_results
                
            # Short circuit if no candidates remain
            if not candidates:
                return []
        
        # Apply prefix lookups (startswith on indexed prefixes)
        for lookup in self.prefix_lookups:
            prefix_index = self._get_prefix_index_for_field(index, lookup.field_name)
            if prefix_index and lookup.value in prefix_index:
                lookup_results = set(prefix_index[lookup.value])
                candidates &= lookup_results
                
            # Short circuit if no candidates remain
            if not candidates:
                return []
        
        # Apply remaining filters in order of estimated cost
        for filter_ in self.remaining_filters:
            candidates = {item for item in candidates if filter_.matches(item)}
            
            # Short circuit if no candidates remain
            if not candidates:
                return []
        
        return list(candidates)
    
    def _get_index_for_field(self, index, field_name):
        """Get the appropriate index for a field"""
        if field_name == 'role':
            return index.role_index
        elif field_name == 'decorator':
            return index.decorator_index
        elif field_name == 'type':
            return index.type_index
        elif field_name == 'module':
            return index.module_index
        return None
        
    def _get_prefix_index_for_field(self, index, field_name):
        """Get the appropriate prefix index for a field"""
        if field_name == 'name':
            return index.name_prefix_index
        elif field_name == 'file_path':
            return index.path_prefix_index
        return None