from typing import Dict, Type
from .webhook_base import WebhookHandler
from ..logging.logger import Logger

class WebhookRouter:
    """Routes incoming webhooks to appropriate handlers."""

    def __init__(self):
        self.logger = Logger()
        self.handlers: Dict[str, Type[WebhookHandler]] = {
            # Add more handlers here as needed
        }

    async def route_webhook(self, event_type: str, payload: dict) -> None:
        """Route webhook to appropriate handler based on event type."""
        handler = self.handlers.get(event_type)
        
        if not handler:
            self.logger.error(f"No handler found for event type: {event_type}")
            raise ValueError(f"Unsupported webhook event type: {event_type}")

        await handler.handle(payload)
