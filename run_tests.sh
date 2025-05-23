#!/bin/bash

# Check if Newman is installed
if ! command -v newman &> /dev/null
then
    echo "Newman is not installed. Installing now..."
    npm install -g newman
    npm install -g newman-reporter-htmlextra
fi

# Create environment file if it doesn't exist
if [ ! -f postman_environment.json ]; then
    echo "Creating Postman environment file..."
    echo '{
        "id": "test-environment",
        "name": "Test Environment",
        "values": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "enabled": true
            }
        ]
    }' > postman_environment.json
fi

# Run tests
echo "Running Postman tests with Newman..."
newman run postman_collection.json -e postman_environment.json

# Generate HTML report
echo "Generating HTML report..."
newman run postman_collection.json -e postman_environment.json -r htmlextra --reporter-htmlextra-export ./newman-report.html

echo "Tests completed. HTML report saved to newman-report.html" 