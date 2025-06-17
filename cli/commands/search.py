from pathlib import Path
from cli.service_container import ServiceContainer
from index.codebase_index import CodebaseIndex
from index.query.query_engine import QueryEngine

def create_cli(index_path=None, codebase_dir=None):
    """Create a CLI environment with configured services.

    Returns:
        tuple: (ServiceContainer, dict of command instances)
    """
    services = ServiceContainer()

    # Set default codebase directory
    if not codebase_dir:
        codebase_dir = Path.cwd()

    # Initialize codebase index
    if index_path and Path(index_path).exists():
        codebase_index = CodebaseIndex.load(index_path)
    else:
        codebase_index = CodebaseIndex(codebase_dir).build()

    # Initialize query engine
    query_engine = QueryEngine(codebase_index)

    # Register services
    services.register("codebase_index", codebase_index)
    services.register("query_engine", query_engine)

    # Import and initialize commands
    from cli.commands import discover_commands
    command_classes = discover_commands()

    # Initialize command instances
    commands = {}
    for name, cmd_class in command_classes.items():
        commands[name] = cmd_class(services=services)

    return services, commands
