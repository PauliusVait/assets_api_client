"""
Asset processing module for Jira Assets API.

This module provides the AssetProcessor class which implements business rules
for processing and updating assets in the Jira Assets API.
"""
from typing import Dict, List, Any, Optional
from jira.assets_client import AssetsClient
from logger import Logger

class AssetProcessor:
    """
    Handles asset updates according to business rules.
    
    This class provides methods to process and update assets according to
    specific business rules, such as formatting asset names based on
    their attributes.
    """
    
    def __init__(self, client: AssetsClient, logger=None):
        """
        Initialize a new AssetProcessor instance.
        
        Args:
            client (AssetsClient): The AssetsClient instance for API interactions
            logger (Logger, optional): A custom logger instance. If not provided,
                a new Logger will be configured.
        """
        self.client = client
        self.logger = logger or Logger.configure()
    
    def process_asset_name(self, asset: Any) -> str:
        """
        Generate asset name according to business rules.
        
        Business rules:
        - Format: "Model - Serial Number - Buyout Price: {price with Euro symbol}"
        - Use ObjectType if Model is not available
        - Include Buyout Price only if Device Age >= 18 months
        
        Args:
            asset (Asset or dict): The asset object or dictionary with attributes
            
        Returns:
            str: The generated asset name
        """
        # Extract attributes
        attributes = asset.attributes if hasattr(asset, 'attributes') else {}
        
        self.logger.debug(f"RAW ATTRIBUTES: {attributes}")
        
        # Get Model or use ObjectType as fallback
        model = attributes.get('Model')
        if not model:
            model = asset.object_type if hasattr(asset, 'object_type') else "Unknown"
            self.logger.debug(f"Using ObjectType '{model}' as Model is not available")
        
        # Get Serial Number
        serial_number = attributes.get('Serial Number', 'Unknown')
        
        # Start building the name
        name_parts = [model, serial_number]
        
        # Process buyout price based on device age - EXPLICIT TYPE HANDLING
        raw_device_age = attributes.get('Device Age')
        buyout_price = attributes.get('Buyout Price')
        
        self.logger.debug(f"RAW VALUES: device_age='{raw_device_age}' ({type(raw_device_age).__name__}), "
                         f"buyout_price='{buyout_price}' ({type(buyout_price).__name__})")
        
        # Convert device_age to a numeric value if it's a string
        device_age = None
        if raw_device_age is not None:
            try:
                device_age = float(raw_device_age)
                self.logger.debug(f"Converted device_age to float: {device_age}")
            except (ValueError, TypeError):
                self.logger.debug(f"Couldn't convert device_age to float, using raw value")
                device_age = raw_device_age
        
        # FORCED COMPARISON LOGIC - explicitly check if device_age >= 18  
        include_buyout = False
        
        if device_age is None:
            self.logger.debug("Device age is None, including buyout price by default")
            include_buyout = True
        elif isinstance(device_age, (int, float)):
            # Explicit numeric comparison with debug logging
            numeric_device_age = float(device_age)
            is_greater_or_equal = numeric_device_age >= 18
            self.logger.debug(f"Numeric comparison: {numeric_device_age} >= 18 = {is_greater_or_equal}")
            
            if is_greater_or_equal:
                self.logger.debug(f"Device age {device_age} is >= 18, INCLUDING buyout price")
                include_buyout = True
            else:
                self.logger.debug(f"Device age {device_age} is < 18, NOT including buyout price")
                include_buyout = False
        else:
            self.logger.debug(f"Device age is non-numeric type: {type(device_age).__name__}, not including buyout price")
            include_buyout = False
        
        # Add buyout price to the name if conditions are met
        if include_buyout and buyout_price is not None:
            buyout_price_str = f"Buyout Price: {buyout_price}€"
            name_parts.append(buyout_price_str)
            self.logger.debug(f"Added buyout price to name: {buyout_price_str}")
        else:
            self.logger.debug(f"Not adding buyout price to name. include_buyout={include_buyout}, buyout_price={buyout_price}")
        
        # Join parts to create the final name
        final_name = " - ".join(name_parts)
        self.logger.debug(f"Final generated asset name: '{final_name}'")
        
        return final_name
    
    def prepare_asset_updates(self, asset_id: int) -> Dict[str, Any]:
        """
        Prepare updates for a single asset based on business rules.
        
        Retrieves the current asset data and generates updates according
        to business rules.
        
        Args:
            asset_id (int): ID of the asset to prepare updates for
            
        Returns:
            dict: Dictionary of attribute name/value pairs for the update
        """
        # Get the current asset data
        asset = self.client.get_object(asset_id)
        if not asset:
            self.logger.error(f"Asset with ID {asset_id} not found")
            return {}
        
        # Generate the new asset name
        new_name = self.process_asset_name(asset)
        
        # Prepare updates dictionary
        updates = {
            "Name": new_name
        }
        
        self.logger.debug(f"Prepared updates for asset {asset_id}: {updates}")
        return updates
    
    def update_single_asset(self, asset_id: int) -> bool:
        """
        Update a single asset based on business rules.
        
        Args:
            asset_id (int): ID of the asset to update
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        try:
            updates = self.prepare_asset_updates(asset_id)
            if not updates:
                return False
            
            # Update the asset
            self.logger.debug(f"Sending update request for asset {asset_id}")
            result = self.client.update_object(asset_id, updates)
            self.logger.info(f"Successfully updated asset {asset_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating asset {asset_id}: {str(e)}")
            return False
    
    def update_multiple_assets(self, asset_ids: List[int]) -> Dict[int, bool]:
        """
        Update multiple assets based on business rules.
        
        Args:
            asset_ids (List[int]): List of asset IDs to update
            
        Returns:
            Dict[int, bool]: Dictionary mapping asset IDs to update status (True=success, False=failure)
        """
        results = {}
        for asset_id in asset_ids:
            results[asset_id] = self.update_single_asset(asset_id)
        
        success_count = sum(1 for status in results.values() if status)
        self.logger.info(f"Updated {success_count} out of {len(asset_ids)} assets")
        return results
