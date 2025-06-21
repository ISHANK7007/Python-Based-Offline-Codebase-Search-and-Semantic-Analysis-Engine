class Filter:
    def matches(self, item):
        raise NotImplementedError("Subclasses must implement matches()")

class RoleFilter(Filter):
    def __init__(self, role_name):
        self.role_name = role_name

    def matches(self, item):
        roles = getattr(item, 'roles', None)
        if roles and isinstance(roles, (list, set)):
            return self.role_name in roles
        return False

class DecoratorFilter(Filter):
    def __init__(self, decorator_name):
        self.decorator_name = decorator_name

    def matches(self, item):
        decorators = getattr(item, 'decorators', None)
        if decorators and isinstance(decorators, (list, set)):
            return self.decorator_name in decorators
        return False
