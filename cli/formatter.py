"""
Output formatting utilities for CLI commands.

This module provides helper functions to format asset data
for display in the command line interface.
"""
from tabulate import tabulate

def format_asset_output(asset):
    """
    Format asset details for output.
    
    Args:
        asset: Asset object to format
        
    Returns:
        str: Formatted string representation of the asset in grid format
    """
    # Base information
    output = [
        ["ID", asset.id],
        ["Name", asset.name],
        ["Type", asset.object_type],
        ["Key", asset.object_key],
        ["Created", asset.created],
        ["Updated", asset.updated],
    ]
    
    # Add attributes section if there are any
    if asset.attributes:
        output.append(["", ""])  # Empty line
        output.append(["Attributes", ""])
        # Sort attributes by name for consistent display
        for name in sorted(asset.attributes.keys()):
            value = asset.attributes[name]
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value if v)
            output.append([name, str(value) if value is not None else ""])
    
    return tabulate(output, tablefmt="grid")
