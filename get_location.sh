#!/bin/bash

# get_location.sh
# Helper script to get GPS location using CoreLocationCLI
# Auto-installs CoreLocationCLI if not found

# Check if CoreLocationCLI is installed
if ! command -v CoreLocationCLI &> /dev/null; then
    echo '{"error": "CoreLocationCLI not installed. Installing via Homebrew..."}' >&2
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo '{"error": "Homebrew not found. Please install Homebrew first: https://brew.sh"}' >&2
        exit 1
    fi
    
    # Install CoreLocationCLI
    brew install CoreLocationCLI &> /dev/null
    
    if [ $? -ne 0 ]; then
        echo '{"error": "Failed to install CoreLocationCLI"}' >&2
        exit 1
    fi
fi

# Get location in JSON format
CoreLocationCLI --json 2>/dev/null

if [ $? -ne 0 ]; then
    echo '{"error": "Failed to get location. Please approve CoreLocationCLI in System Settings > Privacy & Security > Location Services"}' >&2
    exit 1
fi

