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
mkdir -p cache  # For schema cache mentioned in the README

echo "Setup complete! Don't forget to update your .env file."