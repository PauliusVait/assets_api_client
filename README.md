# Jira Assets API Client

A Python client for interacting with the Jira Assets API.

## Setup

1. Make sure you have Python 3.x installed
2. Clone this repository
3. Run the setup script:
   ```bash
   ./setup.sh
   ```
4. Configure your `.env` file with the following variables:
   ```
   JIRA_EMAIL=your.email@company.com
   JIRA_API_TOKEN=your_api_token
   JIRA_SITE_NAME=your-site
   ```

## Project Structure

## Project Structure

```python
.
├── main.py                 # Main CLI entry point for executing commands
├── requirements.txt        # Python package dependencies and versions
├── setup.sh               # Environment setup script (venv, dependencies, dirs)
└── src/                   # Source code root directory
    ├── cli/               # Command-line interface components
    │   ├── commands/      # Individual command implementations (get, update, process)
    │   ├── command_base.py    # Abstract base class for all CLI commands
    │   ├── error_handler.py   # Centralized error handling and formatting 
    │   └── output_formatter.py # Results formatting and table generation
    ├── config.py          # Environment and app configuration management
    ├── jira_core/         # Core business logic and API integration
    │   ├── api/           # API client implementations for Jira REST endpoints
    │   │   ├── asset_query.py     # AQL query execution
    │   │   ├── asset_retrieval.py # Single asset fetching
    │   │   ├── asset_update.py    # Asset updates and modifications
    │   │   └── schema_discovery.py # Object type schema handling
    │   ├── asset_client.py    # High-level asset operations facade
    │   ├── client_base.py     # Base HTTP client with auth and retry logic
    │   ├── services/          # Business logic and processing
    │   │   ├── asset_processor.py # Asset processing rules implementation
    │   │   └── asset_creator.py   # Asset creation business logic
    │   └── exceptions.py      # Custom exception classes
    ├── logging/           # Logging configuration and handlers
    │   └── logger.py      # Centralized logging setup and formatting
    └── webhooks/          # Webhook handlers for external integrations

```

The project follows a layered architecture:

CLI Layer (src/cli/)

Handles user input parsing and validation
Formats output for console display
Implements command-specific logic
Provides error handling and user feedback
Core Layer (src/jira_core/)

Implements core business logic
Manages API communication with Jira
Handles data models and transformations
Processes assets according to business rules
Service Layer (src/jira_core/services/)

Implements business rules for assets
Manages asset lifecycle operations
Handles complex processing workflows
Infrastructure

Configuration (src/config.py)
Logging (src/logging/)
Webhook integration (src/webhooks/)
Key entry points:

main.py: CLI application entry point
setup.sh: One-time environment setup
requirements.txt: Project dependencies

## Usage

Retrieve assets by ID:
```bash
# Get a single asset
python main.py get --id 110653

# Get multiple assets
python main.py get --ids 110653,110654
```

Update assets:
```bash
# Update a single asset
python main.py update --id 110653 --attr "Name=Test Name" --attr "Status=Active" --attr "Buyout Price=" 

# Update multiple assets 
python main.py update --ids 110653,110654,110685,110686,110684,110682,110681,110687,110688,110689,110683,110703 --attr "Status=Active" --attr "Name=Test Name" --attr "Buyout Price="
```

Create assets:
```bash
# Create a single asset
python main.py create --type "MacBook" --attributes '{"Name": "Test Create", "Serial Number": "uniqueSn"}'
```

Execute AQL queries:
```bash
python main.py aql --query 'objectType = "iPhone"'
python main.py aql --query 'objectType = "iPhone" OR objectType = "MacBook"'
python main.py aql --query 'objectType IN ("iPhone", "MacBook")'
```

Enable debug logging:
```bash
python main.py get --id 110653 --debug
```

Process assets with business rules:
```bash
# Process a single asset
python main.py process --id 110653

# Process multiple assets by ID
python main.py process --ids 12345,12346,12347

# Process assets using an AQL query
python main.py process --query 'objectType = "iPhone"'

# Process multiple types of assets
python main.py process --query 'objectType = "Macbook" OR objectType = "iPhone"'
python main.py process --query 'objectType IN ("iPhone", "MacBook")' 

# Refresh schema cache when object types have been renamed in Jira
python main.py process --query 'objectType = "Macbook"' --refresh-cache

# Force recalculation of buyout prices even if they exist
python main.py process --query 'objectType = "Macbook"' --recalculate-buyout
```

## Webhooks

The application supports webhooks for real-time processing of asset updates.

### Webhook Configuration

1. Generate a secure webhook secret:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. Configure webhook settings in your `.env` file:
   ```
   WEBHOOK_ENABLED=true
   WEBHOOK_SECRET=<generated-secret>
   # For local development:
   WEBHOOK_HOST=127.0.0.1
   WEBHOOK_PORT=8000
   # For production:
   WEBHOOK_HOST=<your-public-ip>
   WEBHOOK_PORT=8000
   ```

3. Port Selection:
   - Development: Any free port between 8000-8999 is conventional
   - Production: Consider using a reverse proxy (nginx/Apache) on port 80/443

4. Host Configuration:
   - Development: Use `127.0.0.1` or `localhost`
   - Production: Use your server's public IP or domain name

5. Security Recommendations:
   - Never expose the webhook secret
   - Use HTTPS in production
   - Configure firewall rules to only allow Jira's IP addresses
   - Set up rate limiting on your reverse proxy

### Supported Webhook Events

1. Configure your Jira instance to send webhooks to:
   ```
   http://your-server:8000/webhook
   ```

Supported webhook events:
- `asset.update`: Triggered when an asset is updated in Jira
- More events coming soon...

### Asset Processing Rules

When using the `process` command, assets will be updated according to these business rules:

1. **Device Age Calculation**:
   - Calculated as the number of months between Purchase Date and today
   - Stored as the "Device Age" attribute

2. **Buyout Price Calculation**:
   - Based on Purchase Cost, Device Age, and device type (per company policy)
   - VAT (21%) is added to the purchase cost before applying residual percentage
   - Stored as the "Buyout Price" attribute

3. **Asset Name Formatting**:
   - Format: "{Model} - {Serial Number} - Buyout Price: {price}€" (if age >= 18 months)
   - Format: "{Model} - {Serial Number}" (if age < 18 months)
   - If Model is not available, ObjectType will be used instead
   - If Serial Number is not available, "Unknown" will be used

## Common Errors

- `SchemaError`: Occurs when there's an issue with the Jira schema definition
- `InvalidQueryError`: Occurs when an invalid AQL query is provided
- `AssetNotFoundError`: Occurs when the requested asset doesn't exist
- `InvalidUpdateError`: Occurs when trying to update an asset with invalid data

## Troubleshooting

If you encounter any issues:
1. Ensure your `.env` file has the correct credentials
2. Check that your API token has the necessary permissions
3. Enable debug mode with `--debug` for more detailed logs
4. Try refreshing the schema cache with `--refresh-cache` if object types have changed


