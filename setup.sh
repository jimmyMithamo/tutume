#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
source venv/bin/activate

# Check if pip is available in the virtual environment
if ! command -v pip &> /dev/null
then
    echo "pip could not be found in the virtual environment. Please check your Python installation."
    exit 1
fi

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping dependency installation."
fi

# Done
echo "✅ Setup complete! The virtual environment is now activated."
echo "➡️  You can run the application using 'python3 tutume.py'"
echo "➡️  To deactivate the virtual environment, run 'deactivate'"
