#!/bin/bash
# Linting script for the toy web browser project

set -e

echo "🔍 Running linting checks..."

echo "📋 Running flake8..."
flake8 src/ tests/

echo "🔧 Running mypy..."
mypy src/

echo "📦 Checking import order with isort..."
isort --check-only --diff src/ tests/

echo "🎨 Checking formatting with black..."
black --check src/ tests/

echo "✅ All linting checks passed!"