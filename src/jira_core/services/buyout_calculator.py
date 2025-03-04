"""
Buyout price calculator for Jira Assets.

This module provides the BuyoutCalculator class which implements business rules
for calculating asset buyout prices based on purchase cost and age.
"""
from typing import Dict, Optional, Any
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from ...logging.logger import Logger

class BuyoutCalculator:
    """
    Calculates buyout prices for assets based on depreciation rules.
    
    This class provides methods to calculate buyout prices based on
    purchase cost, device age, and asset type.
    """
    
    # VAT rate (21%)
    VAT_RATE = Decimal('0.21')
    
    # Depreciation table by device type and month
    DEPRECIATION_TABLE = [
        {"month": 1, "Computers": 63.75, "Tablets": 75.25, "Phones": 75.25},
        {"month": 2, "Computers": 61.00, "Tablets": 72.50, "Phones": 72.50},
        {"month": 3, "Computers": 58.25, "Tablets": 69.75, "Phones": 69.75},
        {"month": 4, "Computers": 55.50, "Tablets": 67.00, "Phones": 67.00},
        {"month": 5, "Computers": 52.75, "Tablets": 64.25, "Phones": 64.25},
        {"month": 6, "Computers": 50.00, "Tablets": 61.50, "Phones": 61.50},
        {"month": 7, "Computers": 47.25, "Tablets": 58.75, "Phones": 58.75},
        {"month": 8, "Computers": 44.50, "Tablets": 56.00, "Phones": 56.00},
        {"month": 9, "Computers": 41.75, "Tablets": 53.25, "Phones": 53.25},
        {"month": 10, "Computers": 39.00, "Tablets": 50.50, "Phones": 50.50},
        {"month": 11, "Computers": 36.25, "Tablets": 47.75, "Phones": 47.75},
        {"month": 12, "Computers": 35.00, "Tablets": 45.00, "Phones": 45.00},
        {"month": 13, "Computers": 34.25, "Tablets": 43.75, "Phones": 43.75},
        {"month": 14, "Computers": 33.50, "Tablets": 42.50, "Phones": 42.50},
        {"month": 15, "Computers": 32.75, "Tablets": 41.25, "Phones": 41.25},
        {"month": 16, "Computers": 32.00, "Tablets": 40.00, "Phones": 40.00},
        {"month": 17, "Computers": 31.25, "Tablets": 38.75, "Phones": 38.75},
        {"month": 18, "Computers": 30.50, "Tablets": 37.50, "Phones": 37.50},
        {"month": 19, "Computers": 29.75, "Tablets": 36.25, "Phones": 36.25},
        {"month": 20, "Computers": 29.00, "Tablets": 35.00, "Phones": 35.00},
        {"month": 21, "Computers": 28.25, "Tablets": 33.75, "Phones": 33.75},
        {"month": 22, "Computers": 27.50, "Tablets": 32.50, "Phones": 32.50},
        {"month": 23, "Computers": 26.75, "Tablets": 31.25, "Phones": 31.25},
        {"month": 24, "Computers": 26.00, "Tablets": 30.00, "Phones": 30.00},
        {"month": 25, "Computers": 25.59, "Tablets": 29.59, "Phones": 28.92},
        {"month": 26, "Computers": 25.18, "Tablets": 29.18, "Phones": 27.84},
        {"month": 27, "Computers": 24.77, "Tablets": 28.77, "Phones": 26.76},
        {"month": 28, "Computers": 24.36, "Tablets": 28.36, "Phones": 25.68},
        {"month": 29, "Computers": 23.95, "Tablets": 27.95, "Phones": 24.60},
        {"month": 30, "Computers": 23.54, "Tablets": 27.54, "Phones": 23.52},
        {"month": 31, "Computers": 23.13, "Tablets": 27.13, "Phones": 22.44},
        {"month": 32, "Computers": 22.72, "Tablets": 26.72, "Phones": 21.36},
        {"month": 33, "Computers": 22.31, "Tablets": 26.31, "Phones": 20.28},
        {"month": 34, "Computers": 21.90, "Tablets": 25.90, "Phones": 19.20},
        {"month": 35, "Computers": 21.49, "Tablets": 25.49, "Phones": 18.12},
        {"month": 36, "Computers": 21.00, "Tablets": 25.00, "Phones": 17.00},
        {"month": 37, "Computers": 20.10, "Tablets": 24.10, "Phones": 16.55},
        {"month": 38, "Computers": 19.20, "Tablets": 23.20, "Phones": 16.10},
        {"month": 39, "Computers": 18.30, "Tablets": 22.30, "Phones": 15.65},
        {"month": 40, "Computers": 17.40, "Tablets": 21.40, "Phones": 15.20},
        {"month": 41, "Computers": 16.50, "Tablets": 20.50, "Phones": 14.75},
        {"month": 42, "Computers": 15.60, "Tablets": 19.60, "Phones": 14.30},
        {"month": 43, "Computers": 14.70, "Tablets": 18.70, "Phones": 13.85},
        {"month": 44, "Computers": 13.80, "Tablets": 17.80, "Phones": 13.40},
        {"month": 45, "Computers": 12.90, "Tablets": 16.90, "Phones": 12.95},
        {"month": 46, "Computers": 12.00, "Tablets": 16.00, "Phones": 12.50},
        {"month": 47, "Computers": 11.10, "Tablets": 15.10, "Phones": 12.05},
        {"month": 48, "Computers": 10.20, "Tablets": 14.20, "Phones": 11.60}
    ]
    
    # Minimum rates (as percentage) for devices over 48 months old
    MIN_RATES = {
        "Computers": 10.20,
        "Tablets": 14.20,
        "Phones": 11.60
    }
    
    # Type mapping from object type to category
    TYPE_CATEGORY_MAP = {
        "MacBook": "Computers",
        "Windows/Linux": "Computers",
        "iPhone": "Phones",
        "Android": "Phones",
        "Tablet": "Tablets"
    }
    
    def __init__(self, logger=None):
        """
        Initialize a new BuyoutCalculator instance.
        
        Args:
            logger (Logger, optional): A custom logger instance.
        """
        self.logger = logger or Logger.configure()
    
    def get_device_category(self, object_type: str) -> str:
        """
        Map the object type to a device category.
        
        Args:
            object_type (str): The asset object type
            
        Returns:
            str: Device category (Computers, Phones, or Tablets)
        """
        category = self.TYPE_CATEGORY_MAP.get(object_type)
        if not category:
            self.logger.debug(f"Unknown object type '{object_type}', using Computers category")
            category = "Computers"
        
        self.logger.debug(f"Mapped object type '{object_type}' to category '{category}'")
        return category
    
    def get_residual_percentage(self, months: int, category: str) -> Decimal:
        """
        Get the residual percentage based on device age and category.
        
        Args:
            months (int): Age of device in months
            category (str): Device category (Computers, Phones, or Tablets)
            
        Returns:
            Decimal: Residual percentage (0-100)
        """
        # Cap months at 48 for table lookup
        lookup_month = min(months, 48)
        
        # Find percentage based on month and category
        for entry in self.DEPRECIATION_TABLE:
            if entry["month"] == lookup_month:
                percentage = entry.get(category)
                if percentage is not None:
                    self.logger.debug(f"Found residual percentage {percentage}% for {category} at {months} months")
                    return Decimal(str(percentage))
        
        # If beyond 48 months or not found, use minimum rate
        min_rate = self.MIN_RATES.get(category, 10.20)
        self.logger.debug(f"Using minimum residual percentage {min_rate}% for {category} at {months} months")
        return Decimal(str(min_rate))
    
    def calculate_buyout_price(self, 
                              purchase_cost: Optional[Any], 
                              purchase_date: Optional[str],
                              object_type: str) -> Optional[Decimal]:
        """
        Calculate the buyout price based on purchase cost, date and object type.
        
        Args:
            purchase_cost: Original purchase cost of the asset
            purchase_date: Purchase date in YYYY-MM-DD format
            object_type: Type of the asset
            
        Returns:
            Decimal: Calculated buyout price, or None if inputs are invalid
        """
        if not purchase_cost or not purchase_date or not object_type:
            self.logger.debug("Missing required input for buyout calculation")
            return None
            
        try:
            # Convert purchase cost to Decimal
            if isinstance(purchase_cost, str):
                purchase_cost = Decimal(purchase_cost.replace(',', '.').replace('€', '').strip())
            else:
                purchase_cost = Decimal(str(purchase_cost))
            
            # Calculate device age in months
            device_age_months = self.calculate_months_since_purchase(purchase_date)
            if device_age_months is None:
                return None
                
            # Get device category
            category = self.get_device_category(object_type)
            
            # Add VAT to purchase cost
            cost_with_vat = purchase_cost * (Decimal('1') + self.VAT_RATE)
            
            # Get residual percentage for the given age and category
            residual_percentage = self.get_residual_percentage(device_age_months, category)
            
            # Calculate buyout price as residual percentage of cost with VAT
            buyout_price = (cost_with_vat * (residual_percentage / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            self.logger.debug(
                f"Buyout calculation for {object_type} (category: {category}): "
                f"Original cost = {purchase_cost}, "
                f"With VAT = {cost_with_vat}, "
                f"Age = {device_age_months} months, "
                f"Residual % = {residual_percentage}%, "
                f"Buyout price = {buyout_price}€"
            )
            
            return buyout_price
            
        except (ValueError, TypeError, ArithmeticError) as e:
            self.logger.error(f"Error calculating buyout price: {str(e)}")
            return None
    
    def should_update_buyout_price(self, 
                                  current_buyout: Optional[Any], 
                                  calculated_buyout: Optional[Decimal],
                                  force_update: bool = False) -> bool:
        """
        Determine if the buyout price should be updated.
        
        Args:
            current_buyout: Current buyout price in the system
            calculated_buyout: Newly calculated buyout price
            force_update: Force update regardless of current value
            
        Returns:
            bool: True if buyout price should be updated
        """
        if calculated_buyout is None:
            return False
            
        if force_update:
            self.logger.debug("Force update is enabled, updating buyout price")
            return True
            
        if current_buyout is None:
            self.logger.debug("Current buyout price is missing, update needed")
            return True
            
        # Convert to Decimal for comparison
        try:
            if isinstance(current_buyout, str):
                current_decimal = Decimal(current_buyout.replace(',', '.').replace('€', '').strip())
            else:
                current_decimal = Decimal(str(current_buyout))
                
            # Check if the difference is significant (more than €1)
            diff = abs(current_decimal - calculated_buyout)
            if diff > Decimal('1'):
                self.logger.debug(f"Buyout price difference {diff}€ exceeds threshold, update needed")
                return True
                
            self.logger.debug("Current buyout price is up-to-date")
            return False
                
        except (ValueError, TypeError, ArithmeticError):
            self.logger.debug("Current buyout price format is invalid, update needed")
            return True
    
    def calculate_months_since_purchase(self, purchase_date: str) -> Optional[int]:
        """
        Calculate the number of months between purchase date and today.
        
        Args:
            purchase_date: Purchase date in YYYY-MM-DD format
            
        Returns:
            int: Number of months, or None if date is invalid
        """
        if not purchase_date:
            return None
            
        try:
            purchase_dt = datetime.strptime(purchase_date, '%Y-%m-%d').date()
            today = date.today()
            
            # Calculate years and months difference
            years_diff = today.year - purchase_dt.year
            months_diff = today.month - purchase_dt.month
            
            # Total months
            total_months = years_diff * 12 + months_diff
            
            # Adjust for day of the month
            if today.day < purchase_dt.day:
                # If we haven't reached the same day of the month, subtract one month
                total_months -= 1
                
            return max(0, total_months)
        except (ValueError, TypeError):
            self.logger.error(f"Invalid purchase date format: {purchase_date}, expected YYYY-MM-DD")
            return None
