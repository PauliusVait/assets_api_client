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

```
assets_api_client/
├── cli/               # CLI command handlers
├── jira/              # Jira API integration
│   ├── exceptions.py  # Custom exception classes
│   └── ...
├── logs/              # Log files directory
├── cache/             # Schema cache directory
├── .env               # Environment variables
├── main.py            # Entry point
├── README.md          # This file
├── requirements.txt   # Dependencies
└── setup.sh           # Setup script
```

## Usage

Retrieve assets by ID:
```bash
# Get a single asset
python main.py get --id 12345

# Get multiple assets
python main.py get --ids 12345,12346,12347
```

Update assets:
```bash
# Update a single asset
python main.py update --id 12345 --attr "name=New Name" --attr "status=Active"

# Update multiple assets with the same attributes
python main.py update --ids 12345,12346,12347 --attr "status=Active"
python main.py update --ids 12345,12346 --attr "Name=Test"
```

Execute AQL queries:
```bash
python main.py aql --query 'objectType = "iPhone"'
```

Enable debug logging:
```bash
python main.py get --id 12345 --debug
```

Process assets with business rules:
```bash
# Process a single asset
python main.py process --id 12345

# Process multiple assets by ID
python main.py process --ids 12345,12346,12347

# Process assets using an AQL query
python main.py process --query 'objectType = "iPhone"'

# Process multiple types of assets
python main.py process --query 'objectType = "Macbook" OR objectType = "iPhone"'

# Refresh schema cache when object types have been renamed in Jira
python main.py process --query 'objectType = "Macbook"' --refresh-cache
```

### Asset Processing Rules

When using the `process` command, assets will be updated according to these business rules:

- Asset name will be formatted as: "Model - Serial Number - Buyout Price: {price}€"
- If Model is not available, ObjectType will be used instead
- Buyout Price will only be included if Device Age >= 18 months

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
