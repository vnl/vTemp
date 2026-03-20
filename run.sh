#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Initializing Neural Diagnostic Dashboard..."

# 1. Check if the virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# 3. Install dependencies quietly (unless there's an error)
echo "Installing dependencies..."
pip install -q -r requirements.txt

# 4. Start the application
echo "Starting the application..."
python3 sys_info.py

# 5. Deactivate environment when done (optional but good practice for scripts handling their own state)
deactivate
echo "Dashboard closed. System link severed."
