# services.py
class ServiceContainer:
    """Container for application services and dependencies."""
    
    def __init__(self):
        self._services = {}
    
    def register(self, name, instance):
        """Register a service instance by name."""
        self._services[name] = instance
        return self
    
    def get(self, name):
        """Get a service by name."""
        if name not in self._services:
            raise KeyError(f"Service '{name}' not registered")
        return self._services[name]
    
    def has(self, name):
        """Check if a service exists."""
        return name in self._services