#!/bin/bash
# Render script for the toy web browser project

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Please run 'python -m venv venv && source venv/bin/activate && pip install -r requirements.txt' first."
    exit 1
fi

# Add src to Python path and run the browser
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
python -m src.browser "$@"
