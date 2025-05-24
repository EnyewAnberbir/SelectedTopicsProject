@echo off
echo Checking if Newman is installed...

where newman >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Newman is not installed. Installing now...
    npm install -g newman
    npm install -g newman-reporter-htmlextra
) else (
    echo Newman is already installed.
)

echo Creating Postman environment file...
echo {^
    "id": "test-environment",^
    "name": "Test Environment",^
    "values": [^
        {^
            "key": "base_url",^
            "value": "http://localhost:8000",^
            "enabled": true^
        }^
    ]^
} > postman_environment.json

echo Running Postman tests with Newman...
newman run postman_collection.json -e postman_environment.json

echo Generating HTML report...
newman run postman_collection.json -e postman_environment.json -r htmlextra --reporter-htmlextra-export ./newman-report.html

echo Tests completed. HTML report saved to newman-report.html
pause 