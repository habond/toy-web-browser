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

The browser follows a clean 3-stage rendering pipeline with element-based modularity:

1. **HTML Parser** (`src/html_parser.py`): Converts HTML text → DOM tree
   - Creates `DOMNode` objects with tag, attributes, text, and children
   - Handles self-closing tags and basic HTML structure
   - Supports all major HTML elements including tables

2. **Layout Engine** (`src/layout_engine.py`): DOM tree → layout tree with positions
   - Delegates layout computation to element-specific classes via ElementFactory
   - Computes absolute x,y coordinates and dimensions for each element
   - Handles text wrapping, line spacing, and table layout positioning
   - Uses a simple box model with dynamic image height based on content

3. **Renderer** (`src/renderer.py`): Layout tree → PNG image
   - Delegates rendering to element-specific classes
   - Uses PIL to draw text and basic shapes
   - Loads fonts from `fonts/` directory (OpenSans, SourceCodePro)
   - Handles text formatting and table grids

4. **Element Classes** (`src/elements/`): Modular HTML element implementations
   - **BaseElement**: Abstract base class defining layout() and render() interfaces
   - **ElementFactory**: Factory pattern for creating appropriate element instances
   - **Specialized Elements**: Each HTML tag type has its own class (TextElement, HeadingElement, etc.)
   - **Delegation Pattern**: Layout engine and renderer delegate to element-specific implementations

The main entry point (`src/browser.py`) orchestrates these components and provides CLI argument parsing.

## Key Implementation Details

- **Element-Based Architecture**: Replaced large if-elif chains with modular element classes
- **Factory Pattern**: ElementFactory creates appropriate element instances based on HTML tags
- **Delegation Pattern**: Layout engine and renderer delegate to element-specific implementations
- **Direct Imports**: Simplified import structure without TYPE_CHECKING complexity
- **Flat Structure**: Single-level src/ directory with elements/ subdirectory for element classes
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
├── html_parser.py            # DOMNode, HTMLParser
├── layout_engine.py          # LayoutEngine, LayoutNode, Box
├── renderer.py               # Renderer
└── elements/                  # Element-specific implementations
    ├── __init__.py
    ├── base.py               # BaseElement abstract class
    ├── element_factory.py    # ElementFactory for creating elements
    ├── text.py               # TextElement
    ├── block.py              # BlockElement (div, p, blockquote)
    ├── heading.py            # HeadingElement (h1-h6)
    ├── list.py               # ListElement, ListItemElement
    ├── table.py              # TableElement, TableRowElement, TableCellElement
    ├── inline.py             # InlineElement (b, i, span, a, etc.)
    └── special.py            # BreakElement, HorizontalRuleElement
```