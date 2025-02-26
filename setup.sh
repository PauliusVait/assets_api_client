#!/bin/bash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cat > .env << EOL
JIRA_EMAIL=
JIRA_API_TOKEN=
JIRA_SITE_NAME=

EOL
    echo "Created .env file. Please update it with your credentials."
fi

# Create necessary directories
mkdir -p logs
mkdir -p cache
mkdir -p tests/unit/cli tests/unit/core tests/integration

# Create refactored directory structure
mkdir -p src/cli/commands
mkdir -p src/core/api
mkdir -p src/core/models
mkdir -p src/core/services
mkdir -p src/logging

# Create empty __init__.py files where needed
find src tests -type d | while read dir; do
    touch "$dir/__init__.py"
    echo "Created __init__.py in $dir"
done

echo "Setup complete! Don't forget to update your .env file."