# Toy Web Browser

A simplified web browser that renders basic HTML to PNG images. This educational project demonstrates the core concepts of browser rendering without the complexity of CSS, JavaScript, or network requests.

## Features

- Parses basic HTML tags (headings, paragraphs, lists, tables, formatting)
- Computes layout positions for elements with proper text wrapping
- Renders HTML to PNG images with professional grid-based table borders
- Supports dynamic image sizing based on content
- Clean element-based architecture with modular HTML element classes

## Supported HTML Tags

- **Structure**: `<html>`, `<body>`, `<div>`
- **Headings**: `<h1>` to `<h6>`
- **Text**: `<p>`, `<br>`, `<hr>`
- **Formatting**: `<b>`, `<i>`, `<u>`, `<strong>`, `<em>`, `<code>`
- **Lists**: `<ul>`, `<ol>`, `<li>`
- **Tables**: `<table>`, `<tr>`, `<td>`, `<th>` (with grid borders and header styling)
- **Other**: `<blockquote>`, `<a>`, `<span>`

## Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
./scripts/render.sh <input.html> <output.png> [--output-dir OUTPUT_DIR]
```

Examples:
```bash
# Render to current directory
./scripts/render.sh examples/test1.html output.png

# Render to specific directory
./scripts/render.sh examples/test1.html test1.png --output-dir output_images

# Short form
./scripts/render.sh examples/test2.html test2.png -o output_images
```

The `--output-dir` option allows you to specify a target directory for the output PNG files, keeping your project directory clean.

## Project Structure

```
toy-web-browser/
├── src/                    # Source code
│   ├── __init__.py
│   ├── browser.py         # Main browser logic and CLI
│   ├── html_parser.py     # DOM tree creation
│   ├── layout_engine.py   # Position and size calculation
│   ├── renderer.py        # PNG image generation
│   └── elements/          # Element-specific implementations
│       ├── __init__.py
│       ├── base.py        # Abstract base element class
│       ├── element_factory.py # Factory for creating elements
│       ├── text.py        # Text rendering
│       ├── block.py       # Block elements (div, p, blockquote)
│       ├── heading.py     # Heading elements (h1-h6)
│       ├── list.py        # List elements (ul, ol, li)
│       ├── table.py       # Table elements (table, tr, td, th)
│       ├── inline.py      # Inline elements (b, i, span, a, etc.)
│       └── special.py     # Special elements (br, hr)
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_browser.py    # End-to-end tests
│   ├── test_html_parser.py
│   └── test_layout_engine.py
├── scripts/               # Development scripts
│   ├── format.sh          # Code formatting
│   ├── lint.sh            # Linting checks
│   ├── render.sh          # Render HTML to PNG
│   └── examples.sh        # Render all examples
├── fonts/                 # Project fonts
│   ├── OpenSans-Regular.ttf
│   ├── OpenSans-Bold.ttf
│   ├── SourceCodePro-Regular.ttf
│   └── README.md
├── examples/              # Example HTML files
│   ├── test1.html         # Basic features demo
│   ├── test2.html         # Text formatting
│   ├── test3.html         # Complex nested elements
│   ├── font_test.html     # Font rendering
│   ├── list_test.html     # List examples
│   └── table_test.html    # Table examples
├── output_images/         # Generated PNG files
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Tool configuration
├── .flake8               # Linting configuration
├── CLAUDE.md             # Claude Code instructions
└── README.md
```

## Architecture

The browser follows a clean 3-stage rendering pipeline with element-based modularity:

1. **HTML Parser** (`src/html_parser.py`): Converts HTML text into a DOM tree
   - Creates `DOMNode` objects with tag, attributes, text, and children
   - Handles self-closing tags and basic HTML structure
   - Supports all major HTML elements including tables

2. **Layout Engine** (`src/layout_engine.py`): DOM tree → layout tree with positions
   - Delegates layout computation to element-specific classes
   - Computes absolute x,y coordinates and dimensions for each element
   - Handles text wrapping, line spacing, and table layout
   - Uses a simple box model with configurable viewport width

3. **Renderer** (`src/renderer.py`): Layout tree → PNG image
   - Delegates rendering to element-specific classes
   - Uses PIL to draw text and basic shapes
   - Loads fonts from `fonts/` directory (OpenSans, SourceCodePro)
   - Handles text formatting and table grids

4. **Element Classes** (`src/elements/`): Modular HTML element implementations
   - **BaseElement**: Abstract base class defining layout() and render() interfaces
   - **ElementFactory**: Creates appropriate element instances based on HTML tags
   - **Specialized Elements**: Text, block, heading, list, table, inline, and special elements
   - Each element class handles its own layout computation and rendering logic

## Example Files

The `examples/` directory contains test HTML files:
- `test1.html`: Basic features demo (headings, paragraphs, lists, formatting)
- `test2.html`: Text formatting examples (bold, italic, code, links)
- `test3.html`: Complex nested elements and long text
- `font_test.html`: Font rendering demonstration
- `list_test.html`: List examples (ordered and unordered)
- `table_test.html`: Table examples with headers and data cells

Run all examples at once:
```bash
./scripts/examples.sh
```

## Fonts

The project includes open source fonts from Google Fonts:
- **Open Sans**: Regular and Bold weights for body text and headings
- **Source Code Pro**: Monospace font for code elements

All fonts are included in the `fonts/` directory and are licensed under the SIL Open Font License 1.1.

## Limitations

- No CSS support
- No JavaScript support
- No network requests (local files only)
- Basic font rendering (no font-family CSS)
- Fixed viewport width (800px)
- Tables use equal-width columns only
- No table spanning (colspan/rowspan)

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_browser.py -v
```

### Code Quality

```bash
# Format code (runs isort + black)
./scripts/format.sh

# Run linting (flake8 + mypy + import/formatting checks)
./scripts/lint.sh

# Type checking only
mypy src/

# Individual tools
black src/ tests/                 # Format code
flake8 src/ tests/                # Lint code
isort src/ tests/                 # Sort imports
```