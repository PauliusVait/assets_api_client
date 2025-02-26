Codebase structure before refactoring:
jira-assets-api-client/
│
├── cli/                           # CLI command handlers
│   ├── __init__.py
│   ├── base.py                    # Base command class
│   ├── error_handler.py           # Error handling utilities
│   ├── formatter.py               # Output formatting
│   └── commands/                  # Command implementations
│       ├── __init__.py
│       ├── aql.py                 # AQL query command
│       ├── get.py                 # Get asset command
│       ├── process.py             # Process assets command
│       └── update.py              # Update asset command
│
├── jira/                          # Jira API integration
│   ├── api/                       # API endpoints
│   │   ├── __init__.py
│   │   ├── base_handler.py        # Base request handler
│   │   ├── discover_schema.py     # Schema discovery
│   │   ├── discover_workspace.py  # Workspace discovery
│   │   ├── get_object.py          # Get asset
│   │   ├── get_objects_aql.py     # AQL queries
│   │   └── update_object.py       # Update asset
│   │
│   ├── models/                    # Data models
│   │   ├── asset.py               # Asset model
│   │   └── attribute_mapper.py    # Attribute mapping
│   │
│   ├── services/                  # Empty directory for future use
│   ├── asset_processor.py         # Business logic for asset processing
│   ├── assets_client.py           # Main client implementation  
│   ├── base_client.py             # Base client class
│   └── exceptions.py              # Custom exceptions
│
├── logs/                          # Log files directory
│   ├── assets_api_20250226_155802.log
│   └── assets_api_20250226_155821.log
│
├── .env                           # Environment variables
├── .gitignore                     # Git ignore patterns
├── .vscode/                       # VS Code configuration
│   └── settings.json
├── logger.py                      # Logging configuration
├── main.py                        # Application entry point
├── README.md                      # Documentation
├── requirements.txt               # Dependencies
└── setup.sh                       # Setup script

Codebase structure after refactoring:

jira-assets-api-client/
│
├── src/                           # Root source directory for all application code
│   ├── cli/                       # Command-line interface 
│   │   ├── commands/              # Individual command implementations
│   │   │   ├── __init__.py
│   │   │   ├── aql_command.py     # Renamed for clarity
│   │   │   ├── get_command.py     # Renamed for clarity
│   │   │   ├── process_command.py # Renamed for clarity
│   │   │   └── update_command.py  # Renamed for clarity
│   │   │
│   │   ├── __init__.py
│   │   ├── command_base.py        # Renamed from base.py
│   │   ├── error_handler.py       
│   │   └── output_formatter.py    # Renamed from formatter.py
│   │
│   ├── core/                      # Core business logic (renamed from jira)
│   │   ├── api/                   # API client components
│   │   │   ├── __init__.py
│   │   │   ├── base_handler.py
│   │   │   ├── schema_discovery.py    # Renamed for clarity
│   │   │   ├── workspace_discovery.py # Renamed for clarity
│   │   │   ├── asset_retrieval.py     # Renamed from get_object.py
│   │   │   ├── asset_query.py         # Renamed from get_objects_aql.py
│   │   │   └── asset_update.py        # Renamed from update_object.py
│   │   │
│   │   ├── models/                # Data models
│   │   │   ├── __init__.py
│   │   │   ├── asset.py
│   │   │   └── attribute_mapper.py
│   │   │
│   │   ├── services/              # Service layer between API and CLI
│   │   │   ├── __init__.py
│   │   │   └── asset_processor.py # Moved from root jira/ directory
│   │   │
│   │   ├── __init__.py
│   │   ├── assets_client.py
│   │   ├── client_base.py         # Renamed from base_client.py
│   │   └── exceptions.py
│   │
│   ├── __init__.py
│   ├── config.py                  # Centralized configuration management
│   └── logging/                   # Expanded logging utilities
│       ├── __init__.py
│       └── logger.py              # Moved from root
│
├── tests/                         # Dedicated test directory
│   ├── unit/
│   │   ├── cli/
│   │   └── core/
│   └── integration/
│
├── logs/                          # Log files directory
├── .env                           # Environment variables
├── .gitignore
├── .vscode/
├── main.py                        # Application entry point
├── README.md
├── requirements.txt
└── setup.sh