import argparse
from .get import GetCommand
from .update import UpdateCommand
from .aql import AqlCommand
from .process import ProcessCommand

# Register all commands
COMMANDS = {
    'get': GetCommand(),
    'update': UpdateCommand(),
    'aql': AqlCommand(),
    'process': ProcessCommand()
}

def get_command(name):
    """Get command handler by name"""
    return COMMANDS.get(name)

def register_commands(subparsers):
    """Register all commands with the argument parser"""
    for name, command in COMMANDS.items():
        parser = subparsers.add_parser(
            name, 
            help=f'{name.capitalize()} command',
            formatter_class=command.__class__.__doc__ and argparse.RawDescriptionHelpFormatter or argparse.HelpFormatter
        )
        command.configure_parser(parser)
