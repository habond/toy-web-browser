# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a toy web browser that renders basic HTML to PNG images for educational purposes. It does NOT support CSS, JavaScript, or network requests - only local HTML files with basic tags including tables.

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

The browser follows a clean 3-stage rendering pipeline with modular components:

1. **HTML Parser** (`src/parser/html_parser.py`): Converts HTML text → DOM tree
   - Creates `DOMNode` objects with tag, attributes, text, and children
   - Handles self-closing tags and basic HTML structure
   - Supports all major HTML elements including tables

2. **Layout Engine** (`src/layout/layout_engine.py`): DOM tree → layout tree with positions
   - Computes absolute x,y coordinates and dimensions for each element
   - Handles text wrapping, line spacing, and table layout positioning
   - Uses a simple box model with dynamic image height based on content
   - Specialized table layout with equal-width columns and proper cell sizing

3. **Renderer** (`src/renderer/renderer.py`): Layout tree → PNG image
   - Uses PIL to draw text and basic shapes
   - Loads fonts from `fonts/` directory (OpenSans, SourceCodePro)
   - Handles text formatting (bold, italic, underline, code)
   - Draws complete table grids with connected borders

The main entry point (`src/browser.py`) orchestrates these three components and provides CLI argument parsing.

## Key Implementation Details

- **Modular Structure**: Clean separation into parser, layout, and renderer packages
- **Import Structure**: Uses package imports (`from .parser import HTMLParser`)
- **Font Loading**: Fonts are bundled in `fonts/` directory, not hardcoded paths
- **Output Directory**: PNG files should be directed to `output_images/` directory via `--output-dir`
- **Testing**: Tests use example HTML files and verify PNG generation without pixel-perfect comparisons
- **Type Safety**: Full mypy type checking enabled with strict settings
- **Code Quality**: Automated formatting with black, linting with flake8, import sorting with isort

## Supported HTML Features

Basic structure, headings (h1-h6), paragraphs, lists (ul/ol/li), tables (table/tr/td/th), text formatting (b/i/u/strong/em/code), links, and line breaks. Tables feature equal-width columns, grid borders, and header cell styling. See README.md for complete list.

## Project Structure

```
src/
├── browser.py                 # Main entry point
├── parser/                    # HTML parsing module
│   ├── __init__.py
│   └── html_parser.py        # DOMNode, HTMLParser
├── layout/                    # Layout computation module
│   ├── __init__.py
│   └── layout_engine.py      # LayoutEngine, LayoutNode, Box
└── renderer/                  # Image rendering module
    ├── __init__.py
    └── renderer.py           # Renderer
```