from typing import Any, Dict
from ..webhook_base import WebhookHandler
from ...logging.logger import Logger
from ...jira_core.asset_client import AssetsClient  # Fixed import name

class AssetUpdateWebhookHandler(WebhookHandler):
    """Handler for asset update webhook events."""
    
    def __init__(self):
        self.logger = Logger()
        self.asset_client = AssetsClient()  # Fixed class name

    def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """Validate that the payload contains required fields."""
        required_fields = ['asset_id', 'event_type', 'changes']
        return all(field in payload for field in required_fields)

    async def handle(self, payload: Dict[str, Any]) -> None:
        """Handle asset update webhook event."""
        if not self.validate_payload(payload):
            self.logger.error(f"Invalid webhook payload received: {payload}")
            return

        try:
            asset_id = payload['asset_id']
            self.logger.info(f"Processing webhook for asset {asset_id}")
            
            # Process the asset using existing business logic
            await self.asset_client.process_asset(asset_id)
            
            self.logger.info(f"Successfully processed webhook for asset {asset_id}")
        except Exception as e:
            self.logger.error(f"Error processing webhook: {str(e)}")
            raise
