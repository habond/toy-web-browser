#!/bin/bash
# Formatting script for the toy web browser project

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

# Check if we're in CI or if dependencies are available
if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
    echo "🤖 Running in CI environment, using system Python"
elif [ -d "venv" ]; then
    echo "🐍 Activating virtual environment"
    source venv/bin/activate
else
    # Try to check if dependencies are available globally
    if python -c "import isort, black" 2>/dev/null; then
        echo "📦 Using globally installed dependencies"
    else
        echo "⚠️  Virtual environment not found and formatting tools not available globally."
        echo "Please run 'python -m venv venv && source venv/bin/activate && pip install -r requirements.txt' first."
        exit 1
    fi
fi

echo "🎨 Running code formatting..."

echo "📦 Sorting imports with isort..."
isort src/ tests/

echo "🖤 Formatting code with black..."
black src/ tests/

echo "✅ Code formatting complete!"
