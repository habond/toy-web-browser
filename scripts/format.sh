#!/bin/bash
# Formatting script for the toy web browser project

set -e

echo "🎨 Running code formatting..."

echo "📦 Sorting imports with isort..."
isort src/ tests/

echo "🖤 Formatting code with black..."
black src/ tests/

echo "✅ Code formatting complete!"
