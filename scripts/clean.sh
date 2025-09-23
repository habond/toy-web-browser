#!/bin/bash
# Clean script for the toy web browser project

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

echo "🧹 Cleaning toy web browser project..."

# Check if we're in CI or if dependencies are available
if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
    echo "🤖 Running in CI environment, using system Python"
elif [ -d "venv" ]; then
    echo "🐍 Activating virtual environment"
    source venv/bin/activate
else
    echo "📦 Using global Python installation"
fi

echo "🗑️  Removing Python cache files..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

echo "🗑️  Removing mypy cache..."
rm -rf .mypy_cache/

echo "🗑️  Removing coverage files..."
rm -f .coverage
rm -f coverage.xml
rm -rf htmlcov/

echo "🗑️  Removing build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

echo "🗑️  Removing output images..."
rm -rf output_images/

echo "🗑️  Removing temporary files..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

echo "🗑️  Removing editor temporary files..."
rm -f *.swp
rm -f *.swo

echo "🗑️  Removing log files..."
find . -name "*.log" -delete 2>/dev/null || true

echo "✅ Project cleaned successfully!"
echo ""
echo "📁 Kept essential files:"
echo "   - Source code (src/)"
echo "   - Tests (tests/)"
echo "   - Documentation (README.md, CLAUDE.md)"
echo "   - Configuration files"
echo "   - Virtual environment (venv/)"
echo "   - IDE settings (.vscode/, .idea/)"
