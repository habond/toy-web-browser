"""Pytest configuration and shared fixtures for the toy web browser test suite"""

import tempfile
from pathlib import Path
from typing import Iterator
from unittest.mock import Mock

import pytest
from PIL import Image, ImageDraw, ImageFont

from src.config import BrowserConfig
from src.font_manager import FontManager
from src.html_parser import DOMNode, HTMLParser


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def config() -> BrowserConfig:
    """Provide a test configuration"""
    return BrowserConfig()


@pytest.fixture
def html_parser() -> HTMLParser:
    """Provide an HTML parser instance"""
    return HTMLParser()


@pytest.fixture
def mock_font_manager() -> Mock:
    """Provide a mocked font manager"""
    mock = Mock(spec=FontManager)

    # Create a test font that can be used in tests
    test_font = ImageFont.load_default()
    mock.get_font.return_value = test_font
    mock.default_font = test_font

    return mock


@pytest.fixture
def sample_dom_nodes() -> dict[str, DOMNode]:
    """Provide sample DOM nodes for testing"""
    return {
        "text": DOMNode("text", text="Sample text"),
        "paragraph": DOMNode("p"),
        "heading": DOMNode("h1"),
        "div": DOMNode("div"),
        "span": DOMNode("span"),
        "link": DOMNode("a", attrs={"href": "https://example.com"}),
        "list": DOMNode("ul"),
        "list_item": DOMNode("li"),
        "table": DOMNode("table"),
        "table_row": DOMNode("tr"),
        "table_cell": DOMNode("td"),
        "table_header": DOMNode("th"),
        "break": DOMNode("br"),
        "horizontal_rule": DOMNode("hr"),
    }


@pytest.fixture
def test_image() -> Image.Image:
    """Create a test image for rendering tests"""
    img = Image.new("RGB", (800, 600), "white")
    draw = ImageDraw.Draw(img)
    # Add some basic content to verify the image
    draw.text((10, 10), "Test Image", fill="black")
    return img


@pytest.fixture
def sample_html_content() -> dict[str, str]:
    """Provide sample HTML content for testing"""
    return {
        "simple": "<p>Hello World</p>",
        "heading": "<h1>Title</h1><p>Content</p>",
        "list": "<ul><li>Item 1</li><li>Item 2</li></ul>",
        "table": "<table><tr><th>Header</th></tr><tr><td>Cell</td></tr></table>",
        "nested": "<div><p>Nested <strong>content</strong></p></div>",
        "complex": """
            <!DOCTYPE html>
            <html>
            <head><title>Test</title></head>
            <body>
                <h1>Main Title</h1>
                <p>Introduction paragraph with <a href="#">link</a>.</p>
                <h2>Section</h2>
                <ul>
                    <li>First item</li>
                    <li>Second item</li>
                </ul>
                <table>
                    <tr><th>Name</th><th>Value</th></tr>
                    <tr><td>Test</td><td>123</td></tr>
                </table>
            </body>
            </html>
        """,
    }


@pytest.fixture
def font_files() -> dict[str, Path]:
    """Provide paths to test font files"""
    fonts_dir = Path(__file__).parent.parent / "fonts"
    return {
        "regular": fonts_dir / "DejaVuSans.ttf",
        "bold": fonts_dir / "DejaVuSans-Bold.ttf",
        "italic": fonts_dir / "DejaVuSans-Oblique.ttf",
        "bold_italic": fonts_dir / "DejaVuSans-BoldOblique.ttf",
    }
