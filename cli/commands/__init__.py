# commands/__init__.py
import importlib
import os
import pkgutil
from typing import Dict, Type

from commands.base import Command

def discover_commands() -> Dict[str, Type[Command]]:
    """Automatically discover all command classes in the commands package."""
    commands = {}
    package_path = os.path.dirname(__file__)
    
    for _, module_name, _ in pkgutil.iter_modules([package_path]):
        # Skip the base module and __init__
        if module_name == 'base' or module_name.startswith('__'):
            continue
            
        # Import the module
        module = importlib.import_module(f"commands.{module_name}")
        
        # Find command classes in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            # Check if it's a class, a subclass of Command, and not Command itself
            if (isinstance(attr, type) and 
                issubclass(attr, Command) and 
                attr != Command):
                # Use module_name as the command name
                commands[module_name] = attr
                
    return commands