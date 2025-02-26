"""
Assets API Client Command Line Interface.

This module serves as the entry point for the Assets API Client CLI application.
It handles command-line argument parsing and command execution while providing
appropriate error handling.
"""
import argparse
import sys
from jira.exceptions import SchemaError, InvalidQueryError, AssetNotFoundError, InvalidUpdateError
from cli.commands import register_commands, get_command

def main():
    """
    Main entry point for the CLI application.
    
    Parses command-line arguments, executes the requested command,
    and handles exceptions with appropriate error messages.
    
    Returns:
        None. Exits with status code 0 on success, 1 on failure.
    """
    try:
        # Setup argument parser
        parser = argparse.ArgumentParser(description='Assets API Client CLI')
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Register all commands
        register_commands(subparsers)
        
        # Parse arguments
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            sys.exit(1)
        
        # Get the command handler
        command = get_command(args.command)
        if not command:
            print(f"Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
        
        # Execute the command
        success = command.execute(args)
        sys.exit(0 if success else 1)
            
    except (SchemaError, InvalidQueryError, AssetNotFoundError, InvalidUpdateError) as e:
        # No need to log error type, just show the message
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        # For unexpected errors, show the error type
        print(f"Unexpected error occurred: {type(e).__name__}: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
