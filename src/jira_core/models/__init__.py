"""
Jira Assets API data models package.

This package contains the data models used by the Jira Assets API client.
"""

from .asset import Asset
from .attribute_mapper import AttributeMapper

__all__ = ['Asset', 'AttributeMapper']
