import os
import sys
import importlib
import logging

logger = logging.getLogger(__name__)

class PluginLoader:
    """Load plugins containing custom diff strategies."""

    @classmethod
    def load_plugins(cls, plugin_dir=None):
        """Load all plugins from a directory."""
        if plugin_dir is None:
            plugin_dir = os.path.expanduser("~/.semantic_indexer/plugins")
        
        if not os.path.exists(plugin_dir) or not os.path.isdir(plugin_dir):
            logger.warning(f"Plugin directory not found: {plugin_dir}")
            return

        # Add plugin dir to path so we can import them
        sys.path.insert(0, plugin_dir)

        # Import all .py files in the directory
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                try:
                    importlib.import_module(module_name)
                    logger.info(f"Loaded plugin: {module_name}")
                except Exception as e:
                    logger.error(f"Failed to load plugin {module_name}: {e}", exc_info=True)

        # Remove plugin directory from sys.path to avoid polluting global imports
        sys.path.pop(0)
