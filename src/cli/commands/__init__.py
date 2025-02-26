"""
CLI commands package for the Assets API Client.

This package contains command implementations for the Assets API Client CLI.
"""
import argparse

from .get_command import GetCommand
from .aql_command import AqlCommand
from .update_command import UpdateCommand
from .process_command import ProcessCommand

# Command registry
_COMMANDS = {
    'get': GetCommand,
    'aql': AqlCommand,
    'update': UpdateCommand,
    'process': ProcessCommand,
}

def register_commands(subparsers):
    """
    Register all commands with the argument parser.
    
    Args:
        subparsers: subparsers object from argparse
        
    Returns:
        dict: Dictionary of registered command parsers
    """
    parsers = {}
    for name, command_class in _COMMANDS.items():
        command = command_class()
        parser = subparsers.add_parser(name, help=command.__doc__)
        command.configure_parser(parser)
        parsers[name] = parser
    return parsers

def get_command(name):
    """
    Get a command instance by name.
    
    Args:
        name (str): The name of the command
        
    Returns:
        BaseCommand: An instance of the requested command, or None if not found
    """
    command_class = _COMMANDS.get(name)
    if command_class:
        return command_class()
    return None
