"""
Output formatter for CLI results.

This module provides functions for formatting various types of results
for display in the command-line interface.
"""
from tabulate import tabulate
from typing import List, Dict, Any, Optional

def format_asset(asset: Any) -> str:
    """
    Format an asset object for display.
    
    Args:
        asset: Asset object with attributes
        
    Returns:
        str: Formatted asset details as a string
    """
    if not asset:
        return "No asset found"
    
    # Extract the most important attributes for the top section
    asset_id = str(asset.id) if hasattr(asset, 'id') else ''
    asset_type = asset.object_type if hasattr(asset, 'object_type') else ''
    
    # Extract attributes dict
    attributes = asset.attributes if hasattr(asset, 'attributes') else {}
    
    # Get important attributes with fallbacks
    asset_name = attributes.get('Name', '')
    asset_key = attributes.get('Key', asset.key if hasattr(asset, 'key') else '')
    
    # Summary section with just the most critical info
    summary_table = [
        ["ID", asset_id],
        ["Name", asset_name],
        ["Type", asset_type],
        ["Key", asset_key],
    ]
    
    # Build the full attributes table (sorted alphabetically)
    attributes_table = []
    for key in sorted(attributes.keys()):
        value = attributes.get(key, '')
        attributes_table.append([key, str(value)])
    
    # Combine the tables with a separator
    combined_table = summary_table + [['', ''], ['Attributes', '']] + attributes_table
            
    return tabulate(combined_table, tablefmt="grid")

def format_assets(assets: List[Any]) -> str:
    """
    Format a list of assets for display.
    
    Args:
        assets: List of asset objects
        
    Returns:
        str: Formatted assets list as a string
    """
    if not assets:
        return "No assets found"
    
    table = []
    headers = ["ID", "Name", "Type", "Key"]
    
    for asset in assets:
        name = asset.attributes.get('Name', '') if hasattr(asset, 'attributes') else ''
        object_type = asset.object_type if hasattr(asset, 'object_type') else ''
        key = asset.key if hasattr(asset, 'key') else ''
        asset_id = asset.id if hasattr(asset, 'id') else ''
        
        table.append([asset_id, name, object_type, key])
    
    return tabulate(table, headers=headers, tablefmt="grid")

def format_query_results(results: Dict[str, Any]) -> str:
    """
    Format AQL query results for display.
    
    Args:
        results: Query results dictionary
        
    Returns:
        str: Formatted query results as a string
    """
    if not results or 'values' not in results:
        return "No results found"
    
    values = results.get('values', [])
    return format_assets(values)

def format_process_results(results: Dict[int, bool]) -> str:
    """
    Format asset processing results for display.
    
    Args:
        results: Dictionary mapping asset IDs to success status
        
    Returns:
        str: Formatted processing results as a string
    """
    if not results:
        return "No assets were processed"
    
    total = len(results)
    succeeded = sum(1 for status in results.values() if status)
    
    table = [
        ["Total assets processed", str(total)],
        ["Successfully processed", str(succeeded)],
        ["Failed", str(total - succeeded)]
    ]
    
    return tabulate(table, tablefmt="grid")
