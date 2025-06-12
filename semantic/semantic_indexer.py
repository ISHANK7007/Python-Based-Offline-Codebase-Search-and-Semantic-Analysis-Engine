class SemanticIndexer:
    def __init__(self):
        # Store all processed CodeElements for lookup by ID/name
        self.elements_by_id = {}
        # Additional indices for efficient relationship lookups
        self.function_index = {}  # function_name -> CodeElement
        self.class_index = {}     # class_name -> CodeElement
        # Track pending relationships that need to be resolved
        self.pending_relationships = []
    
    def process_element(self, element):
        """
        Process a single CodeElement, storing it and establishing
        relationships with previously processed elements.
        """
        # Store the element in our indices
        self.index_element(element)
        
        # Augment the element with initial empty relationship collections
        self.initialize_relationship_properties(element)
        
        # Infer and establish relationships based on the element's content
        self.infer_relationships(element)
        
        # Try to resolve any pending relationships that might involve this element
        self.resolve_pending_relationships()
        
        return element
    
    def index_element(self, element):
        # Store in main index
        self.elements_by_id[element.id] = element
        
        # Add to specialized indices based on type
        if element.type == "function":
            self.function_index[element.name] = element
        elif element.type == "class":
            self.class_index[element.name] = element
    
    def initialize_relationship_properties(self, element):
        # Initialize relationship collections if not present
        if not hasattr(element, "calls"):
            element.calls = []
        if not hasattr(element, "called_by"):
            element.called_by = []
        if not hasattr(element, "decorator_roles"):
            element.decorator_roles = {}
    
    def infer_relationships(self, element):
        # Extract function calls from the element
        calls = self.extract_function_calls(element)
        
        # For each called function, establish the relationship
        for called_function_name in calls:
            # Check if we've already seen this function
            if called_function_name in self.function_index:
                called_element = self.function_index[called_function_name]
                # Establish bidirectional relationship
                element.calls.append(called_element)
                called_element.called_by.append(element)
            else:
                # We haven't seen this function yet, add to pending relationships
                self.pending_relationships.append({
                    "type": "call",
                    "caller": element,
                    "callee_name": called_function_name
                })
        
        # Process decorators
        self.process_decorators(element)
    
    def extract_function_calls(self, element):
        """Extract function calls from the element's code."""
        # This would use code analysis to find function calls
        # Simplified example - real implementation would parse the code
        calls = []
        # ... code to extract function calls ...
        return calls
    
    def process_decorators(self, element):
        """Process decorators to establish relationships."""
        if hasattr(element, "decorators") and element.decorators:
            for decorator in element.decorators:
                # Check if decorator is a known function
                if decorator.name in self.function_index:
                    decorator_func = self.function_index[decorator.name]
                    # Add relationship
                    if "decorates" not in decorator_func.decorator_roles:
                        decorator_func.decorator_roles["decorates"] = []
                    decorator_func.decorator_roles["decorates"].append(element)
                else:
                    # Add to pending relationships
                    self.pending_relationships.append({
                        "type": "decorator",
                        "decorated": element,
                        "decorator_name": decorator.name
                    })
    
    def resolve_pending_relationships(self):
        """Try to resolve any pending relationships with newly indexed elements."""
        still_pending = []
        
        for relationship in self.pending_relationships:
            if relationship["type"] == "call":
                callee_name = relationship["callee_name"]
                if callee_name in self.function_index:
                    # We found the called function, establish the relationship
                    caller = relationship["caller"]
                    callee = self.function_index[callee_name]
                    caller.calls.append(callee)
                    callee.called_by.append(caller)
                else:
                    # Still can't resolve this relationship
                    still_pending.append(relationship)
                    
            elif relationship["type"] == "decorator":
                decorator_name = relationship["decorator_name"]
                if decorator_name in self.function_index:
                    # We found the decorator function, establish the relationship
                    decorated = relationship["decorated"]
                    decorator = self.function_index[decorator_name]
                    if "decorates" not in decorator.decorator_roles:
                        decorator.decorator_roles["decorates"] = []
                    decorator.decorator_roles["decorates"].append(decorated)
                else:
                    # Still can't resolve this relationship
                    still_pending.append(relationship)
        
        # Update pending relationships list
        self.pending_relationships = still_pending
    
    def process_stream(self, elements_iterable):
        """Process a stream of CodeElement objects."""
        processed_elements = []
        for element in elements_iterable:
            processed_element = self.process_element(element)
            processed_elements.append(processed_element)
        return processed_elements