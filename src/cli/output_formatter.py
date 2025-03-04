"""
Output formatter for CLI results.

This module provides functions for formatting various types of results
for display in the command-line interface.
"""
from prettytable import PrettyTable
from typing import List, Dict, Any, Optional
from tabulate import tabulate

class OutputFormatter:
    """Centralized formatting utilities for consistent CLI output."""
    
    @staticmethod
    def format_asset_table(assets: List[Any], include_attrs: List[str] = None) -> str:
        """Format assets into a table with consistent columns"""
        headers = ['ID', 'Type', 'Name', 'Key']
        if include_attrs:
            headers.extend(include_attrs)
            
        rows = []
        for asset in assets:
            row = [
                asset.id,
                asset.object_type,
                asset.get_attribute('Name', ''),
                asset.get_attribute('Key', '')
            ]
            if include_attrs:
                row.extend([asset.get_attribute(attr, '') for attr in include_attrs])
            rows.append(row)
            
        return tabulate(rows, headers=headers, tablefmt='grid')
    
    @staticmethod
    def format_results_summary(results: Dict[int, bool]) -> str:
        """Format operation results summary"""
        total = len(results)
        successes = sum(1 for v in results.values() if v)
        failures = total - successes
        
        headers = ['Total', 'Succeeded', 'Failed']
        data = [[total, successes, failures]]
        return tabulate(data, headers=headers, tablefmt='grid')

    @staticmethod
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
        asset_name = attributes.get('Name', '') or getattr(asset, 'name', '')
        asset_key = attributes.get('Key', '') or getattr(asset, 'key', '')
        
        # Create a summary table with critical info
        summary_table = PrettyTable()
        summary_table.field_names = ["Property", "Value"]
        summary_table.add_row(["ID", asset_id])
        summary_table.add_row(["Name", asset_name])
        summary_table.add_row(["Type", asset_type])
        summary_table.add_row(["Key", asset_key])
        
        # Set alignment
        summary_table.align["Property"] = "l"
        summary_table.align["Value"] = "l"
        
        # Create an attributes table
        attr_table = PrettyTable()
        attr_table.field_names = ["Attribute", "Value"]
        
        # Add rows for each attribute (sorted alphabetically)
        for key in sorted(attributes.keys()):
            value = attributes.get(key, '')
            attr_table.add_row([key, str(value)])
        
        # Set alignment
        attr_table.align["Attribute"] = "l"
        attr_table.align["Value"] = "l"
        
        # Combine the output
        return f"{summary_table.get_string()}\n\nAttributes:\n{attr_table.get_string()}"

    @staticmethod
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
        
        table = PrettyTable()
        table.field_names = ["ID", "Name", "Type", "Key"]
        
        for asset in assets:
            name = asset.attributes.get('Name', '') if hasattr(asset, 'attributes') else ''
            if not name and hasattr(asset, 'name'):
                name = asset.name
                
            object_type = asset.object_type if hasattr(asset, 'object_type') else ''
            key = asset.key if hasattr(asset, 'key') else ''
            asset_id = asset.id if hasattr(asset, 'id') else ''
            
            table.add_row([asset_id, name, object_type, key])
        
        # Set alignment
        for field in table.field_names:
            table.align[field] = "l"
        
        return table.get_string()

    @staticmethod
    def format_query_results(results):
        """
        Format query results into a human-readable table.
        
        Args:
            results: List of Asset objects or raw API response
            
        Returns:
            str: Formatted table of query results
        """
        # Check if results is empty
        if not results:
            return "No results found"
        
        # Check what type of results we're dealing with
        if isinstance(results, dict) and 'values' in results:
            # Raw API response with 'values' list
            assets = results.get('values', [])
        elif isinstance(results, list):
            # List of Asset objects
            assets = results
        else:
            # Unexpected type
            return f"Unexpected results type: {type(results)}"
        
        # If no assets found after processing
        if not assets:
            return "No results found"
        
        # Create the table
        table = PrettyTable()
        table.field_names = ['ID', 'Name', 'Type', 'Key']
        
        # Add rows for each asset
        for asset in assets:
            if hasattr(asset, 'to_dict'):
                # This is an Asset object
                asset_dict = asset.to_dict()
                row = [
                    asset_dict.get('id', ''),
                    asset_dict.get('name', ''), 
                    asset_dict.get('type', ''),
                    asset_dict.get('object_key', '')
                ]
            elif isinstance(asset, dict):
                # This is a raw dictionary from API response
                row = [
                    asset.get('id', ''),
                    asset.get('name', ''),
                    asset.get('objectType', {}).get('name', ''),
                    asset.get('objectKey', '')
                ]
            else:
                # Skip unexpected asset types
                continue
                
            table.add_row(row)
        
        # Set alignment
        for field in table.field_names:
            table.align[field] = 'l'
        
        return table.get_string()

    @staticmethod
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
        
        # Create summary statistics
        total = len(results)
        succeeded = sum(1 for status in results.values() if status)
        failed = total - succeeded
        
        # Create a summary table for statistics
        summary_table = PrettyTable()
        summary_table.field_names = ["Metric", "Value"]
        summary_table.add_row(["Total assets processed", str(total)])
        summary_table.add_row(["Successfully processed", str(succeeded)])
        summary_table.add_row(["Failed", str(failed)])
        
        # Set alignment
        summary_table.align["Metric"] = "l"
        summary_table.align["Value"] = "r"
        
        return summary_table.get_string()

    @staticmethod
    def format_process_details(results: Dict[int, bool], assets: List[Any], max_details: int = None) -> str:
        """
        Format details of processed assets for display.
        
        Args:
            results: Dictionary mapping asset IDs to success status
            assets: List of processed assets
            max_details: Maximum number of assets to show details for
            
        Returns:
            str: Formatted details as a string
        """
        if not results or not assets:
            return "No details available"
        
        # Create a lookup table for assets by ID
        asset_map = {str(asset.id): asset for asset in assets if hasattr(asset, 'id')}
        
        # Create a table for asset details
        details_table = PrettyTable()
        details_table.field_names = ["ID", "Name", "Type", "Status"]
        
        # Add a row for each asset, up to max_details if specified
        shown_count = 0
        for asset_id, success in results.items():
            if max_details is not None and shown_count >= max_details:
                break
                
            asset_id_str = str(asset_id)
            if asset_id_str in asset_map:
                asset = asset_map[asset_id_str]
                asset_name = asset.attributes.get('Name', '') if hasattr(asset, 'attributes') else ''
                if not asset_name and hasattr(asset, 'name'):
                    asset_name = asset.name
                asset_type = asset.object_type if hasattr(asset, 'object_type') else ''
            else:
                asset_name = "Unknown"
                asset_type = "Unknown"
            
            status = "✅ Success" if success else "❌ Failed"
            details_table.add_row([asset_id, asset_name, asset_type, status])
            shown_count += 1
        
        # Set alignment
        for field in ["ID", "Name", "Type"]:
            details_table.align[field] = "l"
        details_table.align["Status"] = "c"
        
        # Add a note if we didn't show all assets
        footer = ""
        if max_details is not None and len(results) > max_details:
            footer = f"\n(Showing {max_details} of {len(results)} total assets)"
        
        return details_table.get_string() + footer

    @staticmethod
    def format_update_results(results: Dict[int, bool]) -> str:
        """
        Format asset update results for display.
        
        Args:
            results: Dictionary mapping asset IDs to success status
            
        Returns:
            str: Formatted update results as a string
        """
        if not results:
            return "No assets were updated"
        
        # Create summary statistics
        total = len(results)
        succeeded = sum(1 for status in results.values() if status)
        failed = total - succeeded
        
        # Create a summary table for statistics
        summary_table = PrettyTable()
        summary_table.field_names = ["Metric", "Value"]
        summary_table.add_row(["Total assets updated", str(total)])
        summary_table.add_row(["Successfully updated", str(succeeded)])
        summary_table.add_row(["Failed", str(failed)])
        
        # Set alignment
        summary_table.align["Metric"] = "l"
        summary_table.align["Value"] = "r"
        
        return summary_table.get_string()
