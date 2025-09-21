# Toy Web Browser

A simplified web browser that renders basic HTML to PNG images. This educational project demonstrates the core concepts of browser rendering without the complexity of CSS, JavaScript, or network requests.

## Features

- Parses basic HTML tags (headings, paragraphs, lists, formatting)
- Computes layout positions for elements
- Renders HTML to PNG images
- Supports text wrapping and basic text formatting

## Supported HTML Tags

- **Structure**: `<html>`, `<body>`, `<div>`
- **Headings**: `<h1>` to `<h6>`
- **Text**: `<p>`, `<br>`, `<hr>`
- **Formatting**: `<b>`, `<i>`, `<u>`, `<strong>`, `<em>`, `<code>`
- **Lists**: `<ul>`, `<ol>`, `<li>`
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
│   ├── browser.py         # Main browser logic
│   ├── html_parser.py     # HTML parsing
│   ├── layout_engine.py   # Layout computation
│   └── renderer.py        # PNG rendering
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_browser.py    # End-to-end tests
│   ├── test_html_parser.py
│   └── test_layout_engine.py
├── scripts/               # Development scripts
│   ├── format.sh          # Code formatting
│   ├── lint.sh            # Linting checks
│   └── render.sh          # Render HTML to PNG
├── fonts/                 # Project fonts
│   ├── OpenSans-Regular.ttf
│   ├── OpenSans-Bold.ttf
│   ├── SourceCodePro-Regular.ttf
│   └── README.md
├── examples/              # Example HTML files
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Tool configuration
├── .flake8               # Linting configuration
└── README.md
```

## Architecture

The browser consists of three main components:

1. **HTML Parser** (`src/html_parser.py`): Converts HTML text into a DOM tree
2. **Layout Engine** (`src/layout_engine.py`): Calculates positions and sizes for each element
3. **Renderer** (`src/renderer.py`): Draws the layout tree to a PNG image

## Example Files

The `examples/` directory contains test HTML files:
- `test1.html`: Basic features demo
- `test2.html`: Text formatting examples
- `test3.html`: Complex nested elements and long text
- `font_test.html`: Font rendering demonstration

## Fonts

The project includes open source fonts from Google Fonts:
- **Open Sans**: Regular and Bold weights for body text and headings
- **Source Code Pro**: Monospace font for code elements

All fonts are included in the `fonts/` directory and are licensed under the SIL Open Font License 1.1.

## Limitations

- No CSS support
- No JavaScript support
- No network requests (local files only)
- Basic font rendering
- Fixed viewport width (800px)

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