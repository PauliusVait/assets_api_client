"""
Command module initialization.

This module exposes functions to register commands and retrieve command handlers.
"""
import argparse
from typing import Dict, Optional, Type

from ..command_base import BaseCommand
from .aql_command import AqlCommand
from .get_command import GetCommand
from .process_command import ProcessCommand
from .update_command import UpdateCommand
from .create_command import CreateCommand  # Add import for the new command
from .webhook_command import WebhookCommand  # Add import for the webhook command

# Dictionary mapping command names to command classes
COMMANDS: Dict[str, Type[BaseCommand]] = {
    'aql': AqlCommand,
    'get': GetCommand,
    'process': ProcessCommand,
    'update': UpdateCommand,
    'create': CreateCommand,  # Register the new command
    'webhook': WebhookCommand,  # Add webhook command
}

def register_commands(subparsers) -> None:
    """
    Register all available commands with the argument parser.
    
    Args:
        subparsers: Subparsers object from argparse
    """
    for cmd_name, cmd_class in COMMANDS.items():
        cmd_parser = subparsers.add_parser(cmd_name, help=cmd_class.__doc__)
        cmd_instance = cmd_class()
        cmd_instance.configure_parser(cmd_parser)

def get_command(name: str) -> Optional[BaseCommand]:
    """
    Get a command handler by name.
    
    Args:
        name: Command name
        
    Returns:
        Command handler instance or None if not found
    """
    if name not in COMMANDS:
        return None
    return COMMANDS[name]()
