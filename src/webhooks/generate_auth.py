import base64
import os
import sys
from pathlib import Path

# Add project root to Python path when running directly
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

from src.config import Config

def generate_auth_header():
    """Generate Authorization header for webhook configuration."""
    # Use entire webhook secret as password
    username = 'webhook'
    password = Config.WEBHOOK_SECRET  # Remove [:32] to use full secret
    
    # Combine username and password
    credentials = f"{username}:{password}"
    
    # Base64 encode the credentials
    encoded = base64.b64encode(credentials.encode()).decode()
    
    # Create the Authorization header
    header = f"Basic {encoded}"
    
    print("\nWebhook Authorization Configuration:")
    print("-" * 40)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Authorization Header: {header}")
    print("\nAdd these to your Jira Automation headers:")
    print("Authorization: " + header)
    print("Content-Type: application/json")
    
    return header

if __name__ == "__main__":
    generate_auth_header()
