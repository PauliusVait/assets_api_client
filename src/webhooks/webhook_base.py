from abc import ABC, abstractmethod
from typing import Any, Dict

class WebhookHandler(ABC):
    """Base class for all webhook handlers."""
    
    @abstractmethod
    async def handle(self, payload: Dict[str, Any]) -> None:
        """Handle incoming webhook payload."""
        pass

    @abstractmethod
    def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """Validate incoming webhook payload."""
        pass
