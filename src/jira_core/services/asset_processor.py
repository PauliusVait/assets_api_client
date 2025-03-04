"""
Asset Processing Service for Jira Assets.

This module provides the AssetProcessor class which implements business logic
for processing assets in the Jira Assets system, including recalculation
of buyout prices and other asset-related operations.
"""
from decimal import Decimal
from typing import Dict, Any, Optional
from ...logging.logger import Logger
from ..models.asset import Asset
from .buyout_calculator import BuyoutCalculator

class AssetProcessor:
    """
    Processor for asset business logic operations.
    
    This class handles various operations on assets, including
    calculating buyout prices and updating asset attributes.
    """
    
    def __init__(self, client, logger=None, force_recalculate=False):
        """
        Initialize a new AssetProcessor instance.
        
        Args:
            client: The Assets API client
            logger (Logger, optional): A custom logger instance
            force_recalculate (bool): Force recalculation of buyout prices
                                      even if they already exist
        """
        self.client = client
        self.logger = logger or Logger.configure()
        self.force_recalculate = force_recalculate
        self.buyout_calculator = BuyoutCalculator(logger=self.logger)
        
    def process_asset(self, asset: Asset) -> bool:
        """
        Process an asset according to business rules.
        
        Currently supported operations:
        - Calculate and update buyout price based on purchase cost and age
        - Calculate and update device age
        - Format asset name according to business rules
        
        Args:
            asset: The asset to process
            
        Returns:
            bool: True if the asset was processed successfully
            
        Raises:
            ValueError: If the asset doesn't have required attributes
        """
        self.logger.debug(f"Processing asset {asset.id}")
        
        # Check if this is a buyout-eligible asset
        if not self._is_buyout_eligible(asset):
            self.logger.debug(f"Asset {asset.id} is not eligible for buyout processing")
            return True
            
        # Calculate device age
        purchase_date = asset.attributes.get('Purchase Date')
        device_age_months = self.buyout_calculator.calculate_months_since_purchase(purchase_date)
        
        # Calculate buyout price
        buyout_price = self._calculate_buyout_price(asset)
        
        # Prepare updates dict
        updates = {}
        
        # Update Device Age if available
        if device_age_months is not None:
            updates['Device Age'] = device_age_months
            self.logger.debug(f"Setting Device Age for asset {asset.id} to {device_age_months} months")
        
        # Check if we need to update the buyout price
        current_buyout = asset.attributes.get('Buyout Price')
        buyout_price_updated = False
        if self.buyout_calculator.should_update_buyout_price(
            current_buyout, 
            buyout_price,
            force_update=self.force_recalculate
        ):
            self.logger.info(f"Updating buyout price for asset {asset.id} to {buyout_price}€")
            updates['Buyout Price'] = float(buyout_price)
            buyout_price_updated = True
        
        # Format and update asset name
        current_name = getattr(asset, 'name', None) or asset.attributes.get('Name', '')
        new_name = self._format_asset_name(asset, device_age_months, buyout_price)
        
        # Log the current and new names for debugging
        self.logger.debug(f"Current asset name: '{current_name}'")
        self.logger.debug(f"Formatted new name: '{new_name}'")
        
        # Always update name if buyout price changed or names don't match
        if buyout_price_updated or current_name != new_name:
            self.logger.info(f"Updating asset {asset.id} name from '{current_name}' to '{new_name}'")
            updates['Name'] = new_name
        
        # If we have any updates to make
        if updates:
            self.logger.debug(f"Updating asset {asset.id} with attributes: {list(updates.keys())}")
            # Send the update to the API
            self.client.update_object(asset.id, updates)
            return True
        else:
            self.logger.debug(f"No updates needed for asset {asset.id}")
            return True
            
    def _is_buyout_eligible(self, asset: Asset) -> bool:
        """
        Determine if an asset is eligible for buyout price calculation.
        
        Args:
            asset: The asset to check
            
        Returns:
            bool: True if the asset is eligible for buyout
        """
        # Check if this is a device with purchase information
        if not hasattr(asset, 'attributes'):
            return False
            
        # Get the required attributes
        object_type = asset.object_type if hasattr(asset, 'object_type') else None
        purchase_cost = asset.attributes.get('Purchase Cost')
        purchase_date = asset.attributes.get('Purchase Date')
        
        # Check if we have the required data for buyout calculation
        if not object_type or not purchase_cost or not purchase_date:
            self.logger.debug(
                f"Asset {asset.id} missing required buyout attributes: "
                f"type={object_type}, cost={purchase_cost}, date={purchase_date}"
            )
            return False
            
        # Check if this is a supported device type
        supported_types = self.buyout_calculator.TYPE_CATEGORY_MAP.keys()
        if not any(device_type in object_type for device_type in supported_types):
            self.logger.debug(f"Asset {asset.id} type '{object_type}' is not supported for buyout")
            return False
            
        return True
        
    def _calculate_buyout_price(self, asset: Asset) -> Optional[Decimal]:
        """
        Calculate the buyout price for an asset.
        
        Args:
            asset: The asset to calculate buyout price for
            
        Returns:
            Decimal: The calculated buyout price, or None if calculation fails
        """
        # Extract required attributes
        purchase_cost = asset.attributes.get('Purchase Cost')
        purchase_date = asset.attributes.get('Purchase Date')
        object_type = asset.object_type if hasattr(asset, 'object_type') else ''
        
        # Calculate buyout price
        buyout_price = self.buyout_calculator.calculate_buyout_price(
            purchase_cost=purchase_cost,
            purchase_date=purchase_date,
            object_type=object_type
        )
        
        if buyout_price is None:
            self.logger.warning(f"Failed to calculate buyout price for asset {asset.id}")
            
        return buyout_price
    
    def _format_asset_name(self, asset: Asset, device_age_months: Optional[int], 
                         buyout_price: Optional[Decimal]) -> str:
        """
        Format the asset name according to business rules:
        - Format: "Model - Serial Number - Buyout Price: {price}€" (if age >= 18 months)
        - Format: "Model - Serial Number" (if age < 18 months)
        - If Model is not available, use ObjectType instead
        
        Args:
            asset: The asset to format the name for
            device_age_months: The calculated device age in months
            buyout_price: The calculated buyout price
            
        Returns:
            str: The formatted asset name
        """
        # Get model and serial number
        model = asset.attributes.get('Model')
        if not model or not model.strip():
            model = asset.object_type if hasattr(asset, 'object_type') else "Unknown Device"
            
        serial_number = asset.attributes.get('Serial Number')
        if not serial_number or not serial_number.strip():
            serial_number = "Unknown"
            
        # Start with "Model - Serial Number"
        name_parts = [f"{model} - {serial_number}"]
        
        # Add buyout price if device is 18+ months old and we have a price
        if device_age_months is not None and device_age_months >= 18 and buyout_price is not None:
            name_parts.append(f"Buyout Price: {buyout_price}€")
            
        # Join parts with " - "
        new_name = " - ".join(name_parts)
        self.logger.debug(f"Formatted asset name: {new_name}")
        
        return new_name
