# commands/base.py

from cli.commands.discover_commands import discover_commands

# You can now use discover_commands() without circular import
def main():
    commands = discover_commands()
    ...
