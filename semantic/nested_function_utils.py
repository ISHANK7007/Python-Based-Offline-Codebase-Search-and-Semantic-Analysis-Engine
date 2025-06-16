class BaseSemanticVisitor:
    """Base class for all semantic visitors."""
    def __init__(self, indexer, **kwargs):
        self.indexer = indexer
        
    def analyze(self, element):
        """
        Analyze an element and extract semantic information.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement analyze()")
    
    def visit_node(self, node):
        """
        Visit an AST node. Default implementation does nothing.
        Subclasses should override this method for their specific needs.
        """
        pass