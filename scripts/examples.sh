#!/bin/bash
# Script to render all example HTML files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🎨 Rendering all example files..."

# Create output directory if it doesn't exist
mkdir -p output_images

# Render each example file
for html_file in examples/*.html; do
    if [ -f "$html_file" ]; then
        filename=$(basename "$html_file" .html)
        output_file="${filename}.png"

        echo "📄 Rendering $html_file -> output_images/$output_file"
        ./scripts/render.sh "$html_file" "$output_file" --output-dir output_images
    fi
done

echo "✅ All examples rendered successfully!"
echo "📁 Output files are in the output_images/ directory"