# commands/discover_commands.py

import importlib
import os
import pkgutil
from typing import Dict, Type
from cli.commands.base import Command  # Absolute import to avoid circularity

def discover_commands() -> Dict[str, Type[Command]]:
    """Automatically discover all command classes in the commands package."""
    commands = {}
    package_path = os.path.dirname(__file__)
    
    for _, module_name, _ in pkgutil.iter_modules([package_path]):
        if module_name == 'base' or module_name.startswith('__'):
            continue

        module = importlib.import_module(f"cli.commands.{module_name}")

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, Command) and attr != Command:
                commands[module_name] = attr

    return commands
