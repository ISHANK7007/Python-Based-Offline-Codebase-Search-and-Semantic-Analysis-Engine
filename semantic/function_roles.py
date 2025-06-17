from typing import List, Dict, Any
from models.function import FunctionElement

class FunctionRoleAnalyzer:
    def determine_roles(self, function_element: FunctionElement) -> List[str]:
        roles = []
        
        # Check decorators for role hints (reusing decorator metadata)
        if any(d.name == 'app.route' for d in function_element.decorators):
            roles.append('endpoint')
        
        if any(d.name in ['login_required', 'admin_required'] for d in function_element.decorators):
            roles.append('auth_protected')
        
        # Check function location patterns
        if function_element.file_path.endswith('/tests/'):
            roles.append('test')
        
        if '/api/' in function_element.file_path:
            roles.append('api')
            
        # Check naming conventions
        if function_element.name.startswith('handle_'):
            roles.append('event_handler')
            
        if function_element.name.endswith('_helper'):
            roles.append('helper')
        
        # Check if it's an entry point (e.g., main())
        if function_element.name == 'main' and function_element.is_module_level:
            roles.append('entrypoint')
            
        return roles