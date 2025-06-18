import ast
import builtins
from typing import Dict, Set, List, Optional, Tuple, Any

class CallTargetResolver:
    def __init__(self, semantic_indexer):
        self.indexer = semantic_indexer
        # Store module imports for lookup
        self.module_imports = {}  # module_name -> module instance or import info
        # Store all known symbol aliases
        self.aliases = {}  # alias -> original name
        # Store scope hierarchy
        self.scopes = []  # Stack of scope dictionaries
        # Track wildcard imports
        self.wildcard_imports = set()  # Set of module names with * imports
        # Python builtin functions
        self.builtin_functions = set(dir(builtins))
    
    def resolve_calls_in_function(self, function_element):
        """
        Main entry point to process a function element and resolve all call targets.
        Returns a dictionary of call names to resolved targets.
        """
        # Parse the function body to get AST
        try:
            func_ast = ast.parse(function_element.body)
        except SyntaxError:
            # Handle syntax errors gracefully
            return {}
        
        # Initialize scope for this function
        self.enter_function_scope(function_element)
        
        # Find and resolve all Call nodes
        call_visitor = CallNodeVisitor()
        call_visitor.visit(func_ast)
        
        # Resolve each call to its target
        resolved_calls = {}
        for call_node in call_visitor.calls:
            target_name = self.get_call_target_name(call_node)
            if target_name:
                resolved_target = self.resolve_target(target_name, function_element)
                if resolved_target:
                    resolved_calls[target_name] = resolved_target
        
        # Exit scope when done
        self.exit_scope()
        
        return resolved_calls
    
    def enter_function_scope(self, function_element):
        """Initialize a new scope with function parameters and context."""
        # Create new scope dictionary
        scope = {
            'parameters': self.get_function_parameters(function_element),
            'local_vars': set(),
            'parent_scope': function_element.parent_scope if hasattr(function_element, 'parent_scope') else None
        }
        
        # Process imports in the function context if available
        if hasattr(function_element, 'imports'):
            self.process_imports(function_element.imports)
        
        # Add scope to scope stack
        self.scopes.append(scope)
    
    def exit_scope(self):
        """Exit current scope."""
        if self.scopes:
            self.scopes.pop()
    
    def get_function_parameters(self, function_element):
        """Extract function parameters as a set."""
        params = set()
        if hasattr(function_element, 'parameters'):
            for param in function_element.parameters:
                params.add(param.name)
        return params
    
    def process_imports(self, imports):
        """Process import statements to track modules and aliases."""
        for import_info in imports:
            if import_info.type == 'import':
                # Regular import: import module [as alias]
                module_name = import_info.module
                alias = import_info.alias if hasattr(import_info, 'alias') else module_name
                self.module_imports[alias] = module_name
                
            elif import_info.type == 'from_import':
                # From import: from module import name [as alias]
                module_name = import_info.module
                imported_name = import_info.name
                
                if imported_name == '*':
                    # Wildcard import
                    self.wildcard_imports.add(module_name)
                else:
                    # Regular from import
                    alias = import_info.alias if hasattr(import_info, 'alias') else imported_name
                    qualified_name = f"{module_name}.{imported_name}"
                    self.aliases[alias] = qualified_name
    
    def get_call_target_name(self, call_node):
        """Extract the target name from a Call node."""
        if isinstance(call_node.func, ast.Name):
            # Simple function call: func()
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            # Method or attribute call: obj.method()
            # We need to walk the attribute chain
            current = call_node.func
            parts = []
            
            # Build the chain from right to left
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            
            if isinstance(current, ast.Name):
                parts.append(current.id)
                # Reverse to get the correct order (left to right)
                parts.reverse()
                return '.'.join(parts)
        
        # If we can't determine the name, return None
        return None
    
    def resolve_target(self, target_name, context_element):
        """
        Resolve a target name to an actual CodeElement.
        Handles local variables, imports, aliases, etc.
        """
        # Check if it's a direct function or class reference
        parts = target_name.split('.')
        base_name = parts[0]
        
        # Case 1: Local variable or parameter in current scope
        if self.scopes and (
            base_name in self.scopes[-1]['local_vars'] or 
            base_name in self.scopes[-1]['parameters']
        ):
            # Local variable - we may not be able to resolve this statically
            # Could return a special marker indicating "local variable"
            return {'type': 'local_variable', 'name': base_name}
        
        # Case 2: Imported module or name
        if base_name in self.module_imports:
            module_name = self.module_imports[base_name]
            if len(parts) > 1:
                # This is a module attribute access (module.func)
                qualified_name = f"{module_name}.{'.'.join(parts[1:])}"
                # Try to find in our indexer
                return self.lookup_qualified_name(qualified_name)
            else:
                # Just the module itself
                return {'type': 'module', 'name': module_name}
        
        # Case 3: Aliased import
        if base_name in self.aliases:
            original_name = self.aliases[base_name]
            if len(parts) > 1:
                qualified_name = f"{original_name}.{'.'.join(parts[1:])}"
            else:
                qualified_name = original_name
            return self.lookup_qualified_name(qualified_name)
        
        # Case 4: Built-in function
        if base_name in self.builtin_functions:
            return {'type': 'builtin', 'name': base_name}
        
        # Case 5: Global function or class (directly indexable)
        # First try the exact name
        direct_match = self.lookup_qualified_name(target_name)
        if direct_match:
            return direct_match
        
        # Case 6: Check wildcard imports
        for module_name in self.wildcard_imports:
            qualified_name = f"{module_name}.{target_name}"
            result = self.lookup_qualified_name(qualified_name)
            if result:
                return result
        
        # Case 7: Function in the same module (unqualified)
        if hasattr(context_element, 'module'):
            module_name = context_element.module
            qualified_name = f"{module_name}.{target_name}"
            result = self.lookup_qualified_name(qualified_name)
            if result:
                return result
        
        # If we can't resolve, return a partial resolution with the name
        return {'type': 'unresolved', 'name': target_name}
    
    def lookup_qualified_name(self, qualified_name):
        """Look up a fully qualified name in our indexer."""
        # This would use the indexer to find the element
        # Could check function_index, class_index, etc.
        if qualified_name in self.indexer.function_index:
            return self.indexer.function_index[qualified_name]
        elif qualified_name in self.indexer.class_index:
            return self.indexer.class_index[qualified_name]
        
        # Use additional indexes as needed
        return None


class CallNodeVisitor(ast.NodeVisitor):
    """AST visitor to collect all Call nodes."""
    def __init__(self):
        self.calls = []
    
    def visit_Call(self, node):
        self.calls.append(node)
        self.generic_visit(node)