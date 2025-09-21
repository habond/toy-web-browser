"""Tests for the TextElement class"""

from unittest.mock import Mock, patch

import pytest

from src.config import BrowserConfig
from src.elements.text import TextElement
from src.html_parser import DOMNode
from src.layout_engine import Box, LayoutEngine
from tests.fixtures.test_utils import MockFactory, TestDataBuilder


class TestTextElement:
    """Test the TextElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.mock_font_manager = MockFactory.create_font_manager_mock()
        self.layout_engine = LayoutEngine()

    def test_text_element_creation(self) -> None:
        """Test TextElement can be created"""
        dom_node = DOMNode("text", text="Sample text")
        element = TextElement(dom_node)

        assert element is not None
        assert element.dom_node == dom_node
        assert element.dom_node.text == "Sample text"

    def test_text_element_with_empty_text(self) -> None:
        """Test TextElement with empty text"""
        dom_node = DOMNode("text", text="")
        element = TextElement(dom_node)

        layout_node = element.layout(self.layout_engine, 10, 800)
        assert layout_node is None

    def test_text_element_with_whitespace_only(self) -> None:
        """Test TextElement with whitespace-only text"""
        dom_node = DOMNode("text", text="   \n\t  ")
        element = TextElement(dom_node)

        layout_node = element.layout(self.layout_engine, 10, 800)
        assert layout_node is None

    def test_text_element_layout_basic(self) -> None:
        """Test basic text element layout"""
        dom_node = DOMNode("text", text="Hello World")
        element = TextElement(dom_node)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.dom_node == dom_node
        assert hasattr(layout_node, "box")
        assert hasattr(layout_node, "lines")
        assert layout_node.lines == ["Hello World"]

    def test_text_element_layout_with_wrapping(self) -> None:
        """Test text element layout with text wrapping"""
        long_text = "This is a very long line of text that should wrap when rendered with narrow width"
        dom_node = DOMNode("text", text=long_text)
        element = TextElement(dom_node)

        # Use narrow viewport to force wrapping
        layout_node = element.layout(self.layout_engine, 10, 200)

        assert layout_node is not None
        assert hasattr(layout_node, "lines")
        assert len(layout_node.lines) > 1

    def test_text_element_layout_updates_current_y(self) -> None:
        """Test that text layout updates layout engine current_y"""
        dom_node = DOMNode("text", text="Test text")
        element = TextElement(dom_node)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert self.layout_engine.current_y > initial_y

    def test_text_element_layout_with_custom_max_width(self) -> None:
        """Test text layout with custom max_width parameter"""
        dom_node = DOMNode("text", text="Test text content")
        element = TextElement(dom_node)

        layout_node = element.layout(self.layout_engine, 10, 800, max_width=300)

        assert layout_node is not None
        assert layout_node.box.width == 300

    def test_text_element_render_basic(self) -> None:
        """Test basic text element rendering"""
        dom_node = DOMNode("text", text="Hello World")
        element = TextElement(dom_node)

        # Create layout first
        layout_node = element.layout(self.layout_engine, 10, 800)
        assert layout_node is not None

        # Mock renderer and draw
        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        # Test rendering
        element.render(mock_draw, layout_node, mock_renderer)

        # Should have called text drawing
        mock_draw.text.assert_called()
        mock_renderer._get_font.assert_called()

    def test_text_element_render_multiline(self) -> None:
        """Test text element rendering with multiple lines"""
        long_text = "Line one\nLine two\nLine three"
        dom_node = DOMNode("text", text=long_text)
        element = TextElement(dom_node)

        # Create layout with narrow width to force wrapping
        layout_node = element.layout(self.layout_engine, 10, 200)
        assert layout_node is not None

        # Mock renderer and draw
        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        # Test rendering
        element.render(mock_draw, layout_node, mock_renderer)

        # Should have called text drawing multiple times
        assert mock_draw.text.call_count >= 1

    def test_text_element_render_empty_lines(self) -> None:
        """Test text element rendering handles empty lines"""
        dom_node = DOMNode("text", text="Hello World")
        element = TextElement(dom_node)

        # Create layout
        layout_node = element.layout(self.layout_engine, 10, 800)
        assert layout_node is not None

        # Manually add empty line to test handling
        layout_node.lines = ["Hello World", "", "After empty"]

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        # Test rendering
        element.render(mock_draw, layout_node, mock_renderer)

        # Should skip empty lines (only 2 calls for non-empty lines)
        assert mock_draw.text.call_count == 2

    def test_text_element_render_without_lines(self) -> None:
        """Test text element rendering when layout_node has no lines"""
        dom_node = DOMNode("text", text="Hello World")
        element = TextElement(dom_node)

        # Create layout node without lines attribute
        layout_node = TestDataBuilder.create_layout_node(dom_node)

        mock_renderer = Mock()
        mock_draw = Mock()

        # Test rendering - should not crash
        element.render(mock_draw, layout_node, mock_renderer)

        # Should not call text drawing
        mock_draw.text.assert_not_called()

    def test_text_element_inherits_layout_mixin(self) -> None:
        """Test that TextElement inherits from LayoutMixin"""
        from src.layout_utils import LayoutMixin

        dom_node = DOMNode("text", text="Test")
        element = TextElement(dom_node)

        assert isinstance(element, LayoutMixin)

    @patch("src.elements.text.LayoutUtils.wrap_text")
    @patch("src.elements.text.LayoutUtils.compute_text_height")
    def test_text_element_uses_layout_utils(self, mock_compute_height, mock_wrap_text):
        """Test that TextElement uses LayoutUtils methods"""
        mock_wrap_text.return_value = ["Test line"]
        mock_compute_height.return_value = 24

        dom_node = DOMNode("text", text="Test text")
        element = TextElement(dom_node)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        mock_wrap_text.assert_called_once()
        mock_compute_height.assert_called_once()

    def test_text_element_font_interaction(self) -> None:
        """Test text element interacts correctly with font system"""
        dom_node = DOMNode("text", text="Font test")
        element = TextElement(dom_node)

        layout_node = element.layout(self.layout_engine, 10, 800)
        assert layout_node is not None

        # Mock renderer with specific font
        mock_font = Mock()
        mock_renderer = Mock()
        mock_renderer._get_font.return_value = mock_font
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have requested font from renderer
        mock_renderer._get_font.assert_called_once()

        # Should have used the font in text drawing
        mock_draw.text.assert_called()
        args, kwargs = mock_draw.text.call_args
        assert kwargs.get("font") == mock_font
