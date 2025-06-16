class DecoratorIndex:
    """Specialized index for decorator lookups"""
    
    def __init__(self):
        self.decorator_to_elements = {}  # decorator name -> [elements]
        self.category_to_elements = {}   # category -> [elements]
        self.unresolved = []             # elements with unresolved decorators
    
    def add_element(self, element):
        """Add element to the decorator index"""
        if not hasattr(element, 'decorators') or not element.decorators:
            return
        
        # Index by decorator name
        for decorator in element.decorators:
            # Extract base name without arguments
            base_name = decorator.split('(')[0].lstrip('@')
            
            if base_name not in self.decorator_to_elements:
                self.decorator_to_elements[base_name] = []
            self.decorator_to_elements[base_name].append(element)
        
        # Index by decorator category if available
        if hasattr(element, 'decorator_info') and element.decorator_info:
            has_unresolved = False
            
            for _, info in element.decorator_info.items():
                # Check for category
                if 'category' in info and info['category'] != 'unknown':
                    category = info['category']
                    if category not in self.category_to_elements:
                        self.category_to_elements[category] = []
                    self.category_to_elements[category].append(element)
                
                # Check if unresolved
                if not info.get('resolved', False):
                    has_unresolved = True
            
            if has_unresolved:
                self.unresolved.append(element)
    
    def find_by_decorator(self, decorator_name, include_unresolved=True):
        """Find elements with the given decorator"""
        # Normalize decorator name (strip @ if present)
        decorator_name = decorator_name.lstrip('@')
        
        # Direct lookup by decorator name
        results = self.decorator_to_elements.get(decorator_name, [])
        
        # For unresolved decorators, we need to check each one
        if include_unresolved:
            for element in self.unresolved:
                if any(decorator_name in d for d in element.decorators):
                    if element not in results:  # Avoid duplicates
                        results.append(element)
        
        return results
    
    def find_by_category(self, category):
        """Find elements with decorators in the given category"""
        return self.category_to_elements.get(category, [])