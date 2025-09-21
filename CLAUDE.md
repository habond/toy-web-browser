# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a toy web browser that renders basic HTML to PNG images for educational purposes. It does NOT support CSS, JavaScript, or network requests - only local HTML files with basic tags.

## Common Commands

### Development Workflow
```bash
# Setup virtual environment (first time)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Render HTML to PNG
./scripts/render.sh examples/test1.html output.png --output-dir output_images

# Render all examples at once
./scripts/examples.sh

# Code quality checks
./scripts/format.sh    # Format with black + isort
./scripts/lint.sh      # Run flake8 + mypy + format checks

# Testing
python -m pytest tests/ -v
python -m pytest tests/test_browser.py -v  # Single test file
python -m pytest tests/ --cov=src --cov-report=html  # With coverage
```

### Individual Tools
```bash
mypy src/                    # Type checking only
black src/ tests/            # Code formatting
flake8 src/ tests/           # Linting
isort src/ tests/            # Import sorting
```

## Architecture

The browser follows a classic 3-stage rendering pipeline:

1. **HTML Parser** (`src/html_parser.py`): Converts HTML text → DOM tree
   - Creates `DOMNode` objects with tag, attributes, text, and children
   - Handles self-closing tags and basic HTML structure

2. **Layout Engine** (`src/layout_engine.py`): DOM tree → layout tree with positions
   - Computes absolute x,y coordinates and dimensions for each element
   - Handles text wrapping, line spacing, and list bullet positioning
   - Uses a simple box model with fixed 800px viewport width

3. **Renderer** (`src/renderer.py`): Layout tree → PNG image
   - Uses PIL to draw text and basic shapes
   - Loads fonts from `fonts/` directory (OpenSans, SourceCodePro)
   - Handles text formatting (bold, italic, underline, code)

The main entry point (`src/browser.py`) orchestrates these three components and provides CLI argument parsing.

## Key Implementation Details

- **Import Structure**: Uses relative imports (`.module` not `src.module`)
- **Font Loading**: Fonts are bundled in `fonts/` directory, not hardcoded paths
- **Output Directory**: PNG files can be directed to specific output directories via `--output-dir`
- **Testing**: Tests use example HTML files and verify PNG generation without pixel-perfect comparisons
- **Type Safety**: Full mypy type checking enabled with strict settings

## Supported HTML Features

Basic structure, headings (h1-h6), paragraphs, lists (ul/ol/li), text formatting (b/i/u/strong/em/code), links, and line breaks. See README.md for complete list.