class DecoratorKnowledgeBase:
    def __init__(self):
        # Initialize with built-in decorator knowledge
        self.decorators = {
            # Authentication/Authorization
            'login_required': {
                'category': 'auth',
                'effect': 'Restricts access to authenticated users',
                'frameworks': ['django', 'flask'],
                'security_impact': 'high',
                'properties': {'requires_authentication': True}
            },
            'permission_required': {
                'category': 'auth',
                'effect': 'Restricts access to users with specific permissions',
                'frameworks': ['django'],
                'security_impact': 'high',
                'properties': {'requires_permissions': True}
            },
            'user_passes_test': {
                'category': 'auth',
                'effect': 'Restricts access based on custom user test',
                'frameworks': ['django'],
                'security_impact': 'high',
                'properties': {'requires_custom_check': True}
            },
            
            # Performance
            'lru_cache': {
                'category': 'performance',
                'effect': 'Caches function results with LRU eviction policy',
                'frameworks': ['python-stdlib'],
                'performance_impact': 'high',
                'properties': {'implements_caching': True}
            },
            'cache': {
                'category': 'performance',
                'effect': 'Caches function results',
                'frameworks': ['django'],
                'performance_impact': 'high',
                'properties': {'implements_caching': True}
            },
            
            # Web Framework
            'route': {
                'category': 'web',
                'effect': 'Maps URL route to handler function',
                'frameworks': ['flask', 'bottle'],
                'properties': {'defines_endpoint': True}
            },
            'api_view': {
                'category': 'web',
                'effect': 'Marks function as API endpoint',
                'frameworks': ['drf'],
                'properties': {'defines_api_endpoint': True}
            },
            
            # ORM / Database
            'transaction.atomic': {
                'category': 'database',
                'effect': 'Wraps function in a database transaction',
                'frameworks': ['django'],
                'data_impact': 'high',
                'properties': {'ensures_atomicity': True}
            },
            
            # Testing
            'patch': {
                'category': 'testing',
                'effect': 'Mocks an object during test execution',
                'frameworks': ['unittest.mock'],
                'properties': {'implements_mocking': True}
            },
            
            # Async
            'asyncio.coroutine': {
                'category': 'async',
                'effect': 'Marks function as a coroutine (pre Python 3.5)',
                'frameworks': ['python-stdlib'],
                'properties': {'is_async': True}
            }
        }
        
        # Framework-specific knowledge bases
        self.framework_decorators = {
            'django': {},
            'flask': {},
            'fastapi': {},
            # Add more frameworks as needed
        }
        
        # Project-specific decorators (empty by default)
        self.project_decorators = {}
        
    def get_decorator_info(self, decorator_name, module_path=None):
        """
        Get information about a decorator by name and optional module path.
        Returns the decorator info or None if not found.
        """
        # First check project-specific decorators
        if decorator_name in self.project_decorators:
            return self.project_decorators[decorator_name]
        
        # Then check core decorators
        if decorator_name in self.decorators:
            return self.decorators[decorator_name]
        
        # Try to match based on module path if provided
        if module_path:
            framework = self._infer_framework_from_path(module_path)
            if framework and framework in self.framework_decorators:
                if decorator_name in self.framework_decorators[framework]:
                    return self.framework_decorators[framework][decorator_name]
        
        # Check if it's a qualified name (e.g., "django.contrib.auth.decorators.login_required")
        if '.' in decorator_name:
            parts = decorator_name.split('.')
            simple_name = parts[-1]
            return self.get_decorator_info(simple_name, '.'.join(parts[:-1]))
        
        return None
    
    def add_project_decorator(self, name, metadata):
        """Add or update a project-specific decorator."""
        self.project_decorators[name] = metadata
    
    def load_framework_decorators(self, framework_name):
        """Load decorators for a specific framework."""
        if framework_name == 'django':
            self._load_django_decorators()
        elif framework_name == 'flask':
            self._load_flask_decorators()
        # Add more frameworks as needed
    
    def _infer_framework_from_path(self, module_path):
        """Try to infer which framework a module belongs to."""
        if module_path.startswith('django'):
            return 'django'
        elif module_path.startswith('flask'):
            return 'flask'
        # Add more frameworks as needed
        return None
    
    def _load_django_decorators(self):
        """Load Django-specific decorators."""
        django_decorators = {
            # More specific Django decorator definitions
            'method_decorator': {
                'category': 'util',
                'effect': 'Transforms a function decorator into a method decorator',
                'frameworks': ['django'],
                'properties': {'decorator_transformer': True}
            },
            'csrf_exempt': {
                'category': 'security',
                'effect': 'Exempts a view from CSRF protection',
                'security_impact': 'high',
                'security_risk': True,
                'frameworks': ['django'],
                'properties': {'disables_csrf': True}
            }
            # Add more Django-specific decorators
        }
        self.framework_decorators['django'] = django_decorators
    
    def _load_flask_decorators(self):
        """Load Flask-specific decorators."""
        flask_decorators = {
            # Flask decorator definitions
            'before_request': {
                'category': 'web',
                'effect': 'Registers a function to run before each request',
                'frameworks': ['flask'],
                'properties': {'request_hook': 'before'}
            },
            'after_request': {
                'category': 'web',
                'effect': 'Registers a function to run after each request',
                'frameworks': ['flask'],
                'properties': {'request_hook': 'after'}
            }
            # Add more Flask-specific decorators
        }
        self.framework_decorators['flask'] = flask_decorators
    
    def load_from_file(self, file_path):
        """Load decorator definitions from a JSON or YAML file."""
        import json
        import os
        
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.json'):
                    definitions = json.load(f)
                elif file_path.endswith(('.yaml', '.yml')):
                    import yaml
                    definitions = yaml.safe_load(f)
                else:
                    return False
                
                # Update decorators based on the loaded definitions
                framework = definitions.get('framework', 'project')
                decorators = definitions.get('decorators', {})
                
                if framework == 'project':
                    self.project_decorators.update(decorators)
                elif framework in self.framework_decorators:
                    self.framework_decorators[framework].update(decorators)
                else:
                    self.framework_decorators[framework] = decorators
                    
                return True
        except Exception as e:
            print(f"Error loading decorator definitions: {e}")
            return False