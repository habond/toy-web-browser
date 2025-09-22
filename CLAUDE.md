# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a toy web browser that renders basic HTML to PNG images for educational purposes. It does NOT support CSS, JavaScript, or network requests - only local HTML files with basic tags including tables.

🆕 **Recently Refactored** (2024) with centralized configuration, modular font management, comprehensive error handling, and enhanced modular architecture for improved maintainability. Latest updates include complete modularization of input elements and layout utilities using professional design patterns.

## Common Commands

### Development Workflow
```bash
# Setup virtual environment (first time)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Render HTML to PNG
./scripts/render.sh examples/01_basic_structure.html output.png --output-dir output_images

# Render all examples at once
./scripts/examples.sh

# Code quality checks
./scripts/format.sh    # Format with black + isort
./scripts/lint.sh      # Run flake8 + mypy + format checks
./scripts/clean.sh     # Clean build artifacts and cache files

# Testing (comprehensive test suite with high coverage)
./scripts/test.sh                    # Run all tests with dynamic discovery
./scripts/test.sh -c                # Run tests with coverage report
./scripts/test.sh -c -h             # Run tests with HTML coverage report
./scripts/test.sh -f                # Run only fast unit tests
./scripts/test.sh -v                # Run tests with verbose output
./scripts/test.sh -p test_config    # Run tests matching pattern

# Testing (direct pytest commands)
python -m pytest tests/ -v                              # All tests
python -m pytest tests/integration/ -v                  # Integration tests
python -m pytest tests/unit/ -v                         # Unit tests (majority)
python -m pytest tests/unit/elements/ -v                # Element-specific tests
python -m pytest tests/unit/elements/table/ -v          # Table module tests
python -m pytest tests/test_browser.py -v               # Single test file
python -m pytest tests/ --cov=src --cov-report=html     # With coverage report
```

### Individual Tools
```bash
mypy src/                    # Type checking only (uses pyproject.toml)
black src/ tests/            # Code formatting
flake8 src/ tests/           # Linting
isort src/ tests/            # Import sorting
./scripts/clean.sh           # Clean build artifacts and cache files
pre-commit run --all-files   # Run all quality checks
```

### Pre-commit Hooks
```bash
# Setup and usage (included in requirements.txt)
pre-commit install           # Install hooks (one time)
pre-commit run --all-files   # Run all hooks manually
pre-commit autoupdate        # Update hook versions

# Hooks run automatically on git commit and include:
# - File safety checks (whitespace, EOF, merge conflicts)
# - Import sorting and code formatting
# - Linting and type checking
# - Security scanning
# - Full test suite execution
# - Example rendering validation
```

## Architecture

The browser follows a clean 3-stage rendering pipeline with enhanced modularity and supporting systems:

### Core Pipeline
1. **HTML Parser** (`src/html_parser.py`): Converts HTML text → DOM tree
   - Creates `DOMNode` objects with tag, attributes, text, and children
   - Handles self-closing tags and basic HTML structure
   - Supports all major HTML elements including tables

2. **Layout Engine** (`src/layout_engine.py`): DOM tree → layout tree with positions
   - Delegates layout computation to element-specific classes via ElementFactory
   - Computes absolute x,y coordinates and dimensions for each element
   - Handles text wrapping, line spacing, and table layout positioning
   - Uses centralized configuration for consistent spacing and behavior

3. **Renderer** (`src/renderer.py`): Layout tree → PNG image
   - Delegates rendering to element-specific classes
   - Uses professional FontManager for optimized font loading and caching
   - Handles text formatting and table grids with PIL
   - Configurable dimensions and styling

### Supporting Systems (🆕 New)
4. **Configuration System** (`src/config.py`): Centralized settings management
   - `BrowserConfig` dataclass containing all configurable values
   - Font sizes, margins, padding, viewport dimensions, heading multipliers
   - Single source of truth eliminates magic numbers throughout codebase

5. **Font Management** (`src/font_manager.py`): Professional font handling
   - `FontManager` class handles font loading, caching, and retrieval
   - Supports multiple font styles with intelligent fallbacks
   - Error handling with custom FontError exceptions

6. **Layout Module** (`src/layout/`): Modular layout operations (🆕 Phase 2)
   - **Modular Design**: Split into focused, single-responsibility modules
   - **Text Operations** (`text_operations.py`): Character-based text wrapping and calculations
   - **Font Operations** (`font_operations.py`): Font-aware text measurement and wrapping
   - **Layout Utilities** (`layout_utils.py`): Unified access point for all layout operations
   - **Layout Mixin** (`layout_mixin.py`): Reusable element functionality
   - Eliminates code duplication and improves maintainability

7. **Exception Hierarchy** (`src/exceptions.py`): Comprehensive error handling
   - Custom exceptions: BrowserError, ParseError, LayoutError, RenderError, FontError
   - Better debugging and error reporting throughout the application

8. **Element Classes** (`src/elements/`): Modular HTML element implementations
   - **BaseElement**: Abstract base class defining layout() and render() interfaces
   - **ElementFactory**: Factory pattern for creating appropriate element instances
   - **Specialized Elements**: Each HTML tag type has its own focused class
   - **Input Module** (`src/elements/input/`): Form input elements with strategy pattern (🆕 Phase 2):
     - `InputElement`: Main coordinator using strategy pattern for different input types
     - `TextInputRenderer`: Text-based inputs (text, email, password, url, search)
     - `ButtonInputRenderer`: Button inputs (submit, button, reset)
     - `CheckboxInputRenderer` & `RadioInputRenderer`: Control inputs with checked state
     - `FallbackInputRenderer`: Unknown input types with graceful degradation
     - `InputUtilities`: Shared text truncation and display logic
   - **Table Module** (`src/elements/table/`): Complex table rendering split into components:
     - `TableElement`: Main table coordination and grid rendering
     - `TableRowElement`: Row layout and cell management
     - `TableCellElement`: Individual cell rendering with header styling
     - `TableCalculator`: Column width and dimension calculations

The main entry point (`src/browser.py`) orchestrates these components and provides CLI argument parsing.

## Key Implementation Details

### Core Architecture
- **Element-Based Architecture**: Modular element classes with clean interfaces
- **Factory Pattern**: ElementFactory creates appropriate element instances based on HTML tags
- **Delegation Pattern**: Layout engine and renderer delegate to element-specific implementations
- **Centralized Configuration**: Single source of truth for all settings and constants

### New Architectural Improvements (🆕 2024)
- **Professional Font Management**: Dedicated FontManager with caching and error handling
- **Modular Layout System**: Text and font operations split into focused modules (Phase 2)
- **Strategy Pattern Implementation**: Input elements use strategy pattern for extensibility (Phase 2)
- **Modular Table System**: Complex table rendering split into focused components
- **Exception Hierarchy**: Comprehensive error handling with custom exception types
- **Type Safety**: Enhanced type annotations with Optional handling
- **Single Responsibility**: All modules follow SRP with files under 100 lines

### Development Standards
- **Configuration Management**: Modern pyproject.toml-based tool configuration
- **Type Safety**: Zero suppressions across entire codebase, strict mypy compliance for source AND tests
- **Quality Compliance**: 100% suppression elimination (pylint disable, type: ignore, mypy overrides)
- **Professional Test Patterns**: Proper mocking with patch.object(), comprehensive type annotations
- **Import Structure**: Clean imports with circular import avoidance
- **Directory Organization**: Logical separation with `elements/table/` subdirectory
- **Font Loading**: Professional font management with bundled fonts in `fonts/` directory
- **Output Management**: PNG files directed to `output_images/` directory via `--output-dir`
- **Testing Strategy**: Tests verify functionality without pixel-perfect comparisons
- **Code Quality**: Automated formatting (black), linting (flake8), import sorting (isort)
- **Quality Assurance**: Comprehensive pre-commit hooks prevent issues before commit

## Supported HTML Features

Basic structure, headings (h1-h6), paragraphs, lists (ul/ol/li), tables (table/tr/td/th), text formatting (b/i/u/strong/em/code), interactive elements (button), form inputs (input with text, email, password, URL, search, submit, button, reset, checkbox, radio), links, and line breaks. Tables feature equal-width columns, grid borders, and header cell styling. Form inputs include proper text overflow handling and visual styling. See README.md for complete list.

## Project Structure

```
src/
├── browser.py                 # Main entry point and CLI
├── config.py                  # 🆕 Centralized configuration (BrowserConfig)
├── exceptions.py              # 🆕 Custom exception hierarchy
├── font_manager.py            # 🆕 Professional font management (FontManager)
├── html_parser.py            # DOM tree creation (DOMNode, HTMLParser)
├── layout_engine.py          # Layout computation (LayoutEngine, LayoutNode, Box)
├── renderer.py               # PNG image generation (refactored with FontManager)
├── layout/                    # 🆕 Modular layout operations (Phase 2)
│   ├── __init__.py               # Clean interface exports
│   ├── layout_utils.py           # Unified access point (LayoutUtils)
│   ├── layout_mixin.py           # Element functionality (LayoutMixin)
│   ├── text_operations.py        # Character-based text operations
│   └── font_operations.py        # Font-aware text operations
└── elements/                  # Element-specific implementations
    ├── base.py               # BaseElement abstract class and ElementFactory
    ├── text.py, block.py     # Text and block elements (div, p, blockquote)
    ├── heading.py            # Heading elements (h1-h6, size multipliers)
    ├── list.py               # List elements (ul, ol, li)
    ├── inline.py             # Inline elements (b, i, span, a, code, etc.)
    ├── button.py             # Button elements with background styling
    ├── pre.py                # Preformatted text elements
    ├── special.py            # Special elements (br, hr)
    ├── input/                # 🆕 Modular input implementation (Phase 2)
    │   ├── __init__.py              # Clean interface exports
    │   ├── input_element.py         # Main coordinator with strategy pattern
    │   ├── base_input.py            # Abstract base and shared utilities
    │   ├── text_input.py            # Text-based input renderers
    │   ├── button_input.py          # Button input renderers
    │   ├── control_input.py         # Checkbox/radio input renderers
    │   └── fallback_input.py        # Unknown input type handling
    └── table/                # 🆕 Modular table implementation
        ├── table_element.py      # Main table coordination and grid rendering
        ├── table_row_element.py  # Row layout and cell management
        ├── table_cell_element.py # Cell rendering with header styling
        └── table_calculator.py   # Column width and dimension calculations
```

## Testing Infrastructure (🆕 2024)

The project includes comprehensive testing infrastructure with high code coverage and comprehensive test suite:

### Test Organization
```
tests/
├── unit/                    # Comprehensive unit tests for all modules
│   ├── test_config.py          # Configuration system testing
│   ├── test_font_manager.py    # Font management testing
│   ├── test_layout_utils.py    # Layout utilities testing
│   ├── test_renderer.py       # Renderer testing
│   └── elements/            # Element-specific testing (factory, all HTML elements)
│       └── table/               # Complete table module testing (4 test files)
├── integration/             # End-to-end pipeline tests
├── fixtures/                # Professional test infrastructure (MockFactory, TestDataBuilder)
├── conftest.py             # Pytest configuration with shared fixtures
├── test_browser.py         # Original integration tests (maintained)
├── test_html_parser.py     # HTML parser tests
└── test_layout_engine.py   # Layout engine tests
```

### Test Script Usage
```bash
# Quick tests (recommended for development)
./scripts/test.sh -f                # Fast unit tests only (~0.2s)

# Full testing workflow
./scripts/test.sh                   # All tests with dynamic discovery
./scripts/test.sh -c               # With coverage report
./scripts/test.sh -c -h            # With HTML coverage report

# Specific testing
./scripts/test.sh -p config        # Run config tests only
./scripts/test.sh -p table         # Run table tests only
./scripts/test.sh -v               # Verbose output
./scripts/test.sh --help           # Show all options
```

### Coverage & Quality Achievements
- **High Coverage**: Comprehensive test coverage with significant improvement from initial implementation
- **Extensive Test Suite**: Dramatically expanded from initial basic tests to comprehensive coverage
- **Code Quality**: Zero flake8 violations, zero mypy errors
- **Import Standards**: Perfect import ordering and grouping
- **Test Infrastructure**: Professional fixtures, mocks, and utilities
- **Dynamic Discovery**: Automatic test detection as codebase grows

## Refactoring Guidelines

When making changes to this codebase, follow these principles established during the 2024 refactoring:

1. **Use Centralized Configuration**: Import settings from `config.py` rather than hardcoding values
2. **Leverage FontManager**: Use the FontManager class for all font-related operations
3. **Apply Layout Module**: Import from `src.layout` for LayoutUtils and LayoutMixin operations
4. **Handle Errors Properly**: Use custom exceptions from `exceptions.py` for specific error types
5. **Maintain Modularity**: Keep specialized changes within appropriate modules:
   - Table-related: `elements/table/` module
   - Input-related: `elements/input/` module
   - Layout operations: `layout/` module
6. **Follow Design Patterns**: Use strategy pattern for extensible functionality (see input elements)
7. **Single Responsibility**: Keep modules focused and manageable in size
8. **Follow Type Safety**: Maintain proper type annotations, especially for Optional parameters
9. **Preserve Test Coverage**: Ensure all changes maintain the existing comprehensive test suite

## Configuration Access Patterns

```python
# CORRECT: Use centralized config
from ..config import config
font_size = config.DEFAULT_FONT_SIZE
margin = config.MARGIN

# INCORRECT: Hardcoded values
font_size = 16
margin = 10
```

## Font Management Patterns

```python
# CORRECT: Use FontManager
from ..font_manager import FontManager
font_manager = FontManager()
font = font_manager.get_font(size=18, bold=True)

# INCORRECT: Direct PIL font loading
font = ImageFont.truetype("path/to/font.ttf", 18)
```

## Recent Refactoring Summary (2024)

The project underwent comprehensive refactoring to transform it from an educational example into an enterprise-grade codebase:

### ✅ Phase 1: Core Architecture (Completed)
1. **Centralized Configuration** (`config.py`): Eliminated magic numbers, single source of truth
2. **Professional Font Management** (`font_manager.py`): Extracted from renderer, added caching
3. **Layout Utilities** (`layout_utils.py`): Reusable text wrapping and dimension calculations
4. **Exception Hierarchy** (`exceptions.py`): Custom exceptions for better error handling
5. **Modular Table System** (`elements/table/`): Split 281-line file into focused components

### ✅ Phase 2: Quality Engineering (Completed)
6. **Pre-commit Hooks**: Comprehensive automated quality assurance pipeline
7. **Type Safety**: Strict mypy configuration with zero error suppressions in source code
8. **Configuration Consolidation**: Eliminated duplicate configs (removed mypy.ini), modern pyproject.toml
9. **Enhanced .gitignore**: Modern development tool coverage (.ruff_cache, .env files, etc.)
10. **Documentation**: Updated README.md and CLAUDE.md with new architecture

### ✅ Phase 3: Testing Excellence (Completed)
11. **Comprehensive Test Suite**: Dramatically expanded test coverage from minimal initial tests
12. **Testing Infrastructure**: Built professional fixtures, mocks, and test utilities (TestDataBuilder, MockFactory)
13. **Dynamic Test Discovery**: Automated test detection with pattern-based inclusion
14. **Element Coverage**: Complete testing for all HTML element classes and table module
15. **Import Organization**: Perfect import ordering and grouping standards (I101, I201 compliance)
16. **Quality Assurance**: Zero flake8 violations, zero mypy errors, professional code standards

### ✅ Phase 4: Perfect Quality Compliance (Completed 2024)
17. **Zero Suppressions**: Eliminated all quality suppressions (pylint disable, type: ignore, mypy overrides)
18. **Perfect Type Safety**: Complete mypy compliance for both source code AND tests (comprehensive test type errors fixed)
19. **Professional Test Patterns**: Replaced all improper mocking with proper patch.object() context managers
20. **Comprehensive Type Annotations**: Added missing type annotations throughout test functions and variables
21. **Union Type Safety**: Fixed all Optional/Union attribute access patterns with proper null checks

### ✅ Phase 5: Modular Architecture Refactoring (Completed 2024)
22. **Input Element Modularization**: Split large input.py into focused, single-responsibility modules
    - Strategy pattern implementation with specialized renderers for each input type
    - Clean separation: TextInputRenderer, ButtonInputRenderer, CheckboxInputRenderer, etc.
    - Graceful fallback handling for unknown input types
23. **Layout Utilities Modularization**: Split large layout_utils.py into logical modules
    - TextOperations: Character-based text wrapping and calculations
    - FontOperations: Font-aware text measurement and wrapping
    - LayoutMixin: Element-specific layout functionality
    - LayoutUtils: Unified access point maintaining backward compatibility
24. **Single Responsibility Principle**: All modules follow SRP with manageable file sizes
25. **Eliminated Wrapper Dependencies**: Removed unnecessary layout_utils.py wrapper for cleaner imports

### 📊 Impact Achieved
- **Maintainability**: Significantly improved through modular architecture and reduced file complexity
- **Code Quality**: Zero flake8 violations, zero mypy errors, perfect import organization
- **Type Safety**: Comprehensive type annotations with strict checking (zero suppressions in source AND tests)
- **Quality Compliance**: Complete suppression elimination across entire codebase
- **Test Quality**: Professional test patterns with proper mocking and complete type safety
- **Developer Experience**: Automated quality checks and modular architecture for easier development
- **Configuration**: Modern tool configuration without duplicates
- **Testing**: Dramatically expanded test coverage and comprehensive test suite
- **Architecture**: Professional design patterns (Strategy, Factory) with single-responsibility modules
- **Extensibility**: Easy to add new input types and layout operations through modular design

**Before**: Good educational example with basic structure
**After**: Enterprise-grade codebase with professional tooling and practices

All refactoring maintained backward compatibility - the public API remains unchanged.
