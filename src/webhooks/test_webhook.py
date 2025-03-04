import hmac
import hashlib
import requests
import json
from ..config import Config

def send_test_webhook(url="http://localhost:8000/"):
    """Send a test webhook with proper signature."""
    
    # Test payload
    payload = {
        "asset_id": "12345",
        "event_type": "asset.update",
        "changes": {
            "field": "Name",
            "from": "Old Name",
            "to": "New Name"
        }
    }
    
    # Convert payload to JSON string
    body = json.dumps(payload)
    
    # Calculate signature
    signature = 'sha256=' + hmac.new(
        Config.WEBHOOK_SECRET.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'X-Hub-Signature-256': signature,
        'X-Webhook-Event': 'asset.update'
    }
    
    # Send request
    response = requests.post(url, data=body, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    return response

if __name__ == "__main__":
    send_test_webhook()
