class SemanticFunctionDiff:
    """
    Represents semantic differences between two versions of a function.
    Provides granular flags for specific types of changes and detailed change information.
    """
    def __init__(self, symbol, version1=None, version2=None):
        # Basic metadata
        self.symbol = symbol                  # Full symbol path (e.g., 'module.Class.method')
        self.version1 = version1 or "v1"      # Label/identifier for first version
        self.version2 = version2 or "v2"      # Label/identifier for second version
        
        # Simple change flags
        self.exists_in_both = True            # Whether function exists in both versions
        self.signature_changed = False        # Any signature changes (args, returns, etc.)
        self.body_changed = False             # Whether function body changed
        self.doc_changed = False              # Whether docstring changed
        
        # Detailed changes with specific information
        self.changes = {
            # Decorators
            'decorators': {
                'added': [],                  # List of added decorator names
                'removed': [],                # List of removed decorator names
                'modified': []                # List of modified decorators with before/after
            },
            
            # Arguments
            'arguments': {
                'added': [],                  # Added arguments (name, default, type)
                'removed': [],                # Removed arguments (name, default, type)
                'modified': []                # Modified arguments with specifics
            },
            
            # Return information
            'returns': {
                'type_changed': False,        # Whether return type annotation changed
                'before_type': None,          # Previous return type annotation
                'after_type': None            # New return type annotation
            },
            
            # Function body
            'body': {
                'lines_added': 0,             # Count of added lines
                'lines_removed': 0,           # Count of removed lines
                'complexity_before': 0,       # Cyclomatic complexity before
                'complexity_after': 0         # Cyclomatic complexity after
            },
            
            # Docstring
            'docstring': {
                'changed': False,             # Whether docstring changed at all
                'before': None,               # Previous docstring
                'after': None,                # New docstring
                'params_changed': False       # Whether param docs changed
            },
            
            # Semantic relationships
            'relationships': {
                'callers_added': [],          # New functions calling this one
                'callers_removed': [],        # Functions no longer calling this one
                'callees_added': [],          # New functions called by this one
                'callees_removed': []         # Functions no longer called by this one
            }
        }
        
        # Change impact assessment
        self.impact = {
            'api_breaking': False,            # Whether change breaks API compatibility
            'behavior_changing': False,       # Whether semantic behavior likely changed
            'score': 0.0                      # Numeric score of change significance (0-1)
        }
    
    def set_decorator_changes(self, added=None, removed=None, modified=None):
        """Update decorator changes with specific information"""
        if added:
            self.changes['decorators']['added'] = added
        if removed:
            self.changes['decorators']['removed'] = removed
        if modified:
            self.changes['decorators']['modified'] = modified
        
        # Update flags based on changes
        if added or removed or modified:
            self.signature_changed = True
    
    def set_argument_changes(self, added=None, removed=None, modified=None):
        """Update argument changes with specific information"""
        if added:
            self.changes['arguments']['added'] = added
        if removed:
            self.changes['arguments']['removed'] = removed
        if modified:
            self.changes['arguments']['modified'] = modified
        
        # Update flags based on changes
        if added or removed or modified:
            self.signature_changed = True
            # API breaking if required args added or any removed
            self.impact['api_breaking'] = bool(removed) or any(
                not arg.get('has_default', False) for arg in (added or [])
            )
    
    def calculate_impact_score(self):
        """Calculate overall impact score based on all changes"""
        score = 0.0
        weights = {
            'signature': 0.4,
            'body': 0.3,
            'docstring': 0.1,
            'relationships': 0.2
        }
        
        # Apply weights to different change types
        if self.signature_changed:
            score += weights['signature']
        
        if self.body_changed:
            body_change_ratio = (
                (self.changes['body']['lines_added'] + self.changes['body']['lines_removed']) / 
                max(1, self.changes['body'].get('total_lines', 10))
            )
            score += weights['body'] * min(1.0, body_change_ratio)
        
        if self.doc_changed:
            score += weights['docstring']
        
        # Relationship changes
        relationship_changes = (
            len(self.changes['relationships']['callers_added']) +
            len(self.changes['relationships']['callers_removed']) +
            len(self.changes['relationships']['callees_added']) +
            len(self.changes['relationships']['callees_removed'])
        )
        if relationship_changes > 0:
            score += weights['relationships'] * min(1.0, relationship_changes / 5.0)
        
        self.impact['score'] = min(1.0, score)
        return self.impact['score']
    
    def to_dict(self):
        """Convert to dictionary representation for serialization"""
        return {
            'symbol': self.symbol,
            'version1': self.version1,
            'version2': self.version2,
            'exists_in_both': self.exists_in_both,
            'signature_changed': self.signature_changed,
            'body_changed': self.body_changed,
            'doc_changed': self.doc_changed,
            'changes': self.changes,
            'impact': self.impact
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary representation"""
        instance = cls(data['symbol'], data['version1'], data['version2'])
        instance.exists_in_both = data['exists_in_both']
        instance.signature_changed = data['signature_changed']
        instance.body_changed = data['body_changed']
        instance.doc_changed = data['doc_changed']
        instance.changes = data['changes']
        instance.impact = data['impact']
        return instance
    
    def __str__(self):
        """String representation for display"""
        parts = [f"SemanticFunctionDiff: {self.symbol} ({self.version1} → {self.version2})"]
        
        # Add change flags
        flags = []
        if self.signature_changed:
            flags.append("signature_changed=True")
        if self.body_changed:
            flags.append("body_changed=True")
        if self.doc_changed:
            flags.append("doc_changed=True")
        
        if flags:
            parts.append("Changes: " + ", ".join(flags))
        
        # Add specific changes
        if self.changes['decorators']['added']:
            parts.append(f"decorator_added={self.changes['decorators']['added']}")
        if self.changes['decorators']['removed']:
            parts.append(f"decorator_removed={self.changes['decorators']['removed']}")
        
        if self.changes['arguments']['added']:
            parts.append(f"args_added={[a.get('name') for a in self.changes['arguments']['added']]}")
        if self.changes['arguments']['removed']:
            parts.append(f"args_removed={[a.get('name') for a in self.changes['arguments']['removed']]}")
        
        # Add impact assessment
        parts.append(f"impact_score={self.impact['score']:.2f}")
        if self.impact['api_breaking']:
            parts.append("api_breaking=True")
        
        return "\n".join(parts)