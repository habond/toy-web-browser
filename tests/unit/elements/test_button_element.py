"""Tests for the ButtonElement class"""

from unittest.mock import Mock

from src.config import BrowserConfig
from src.elements.button import ButtonElement
from src.html_parser import DOMNode
from src.layout_engine import Box, LayoutEngine
from tests.fixtures.test_utils import MockFactory


class TestButtonElement:
    """Test the ButtonElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.mock_font_manager = MockFactory.create_font_manager_mock()
        self.layout_engine = LayoutEngine()

    def test_button_element_creation(self) -> None:
        """Test ButtonElement can be created"""
        dom_node = DOMNode("button")
        element = ButtonElement(dom_node)

        assert element is not None
        assert element.dom_node == dom_node

    def test_button_element_with_text(self) -> None:
        """Test ButtonElement with text content"""
        button_dom = DOMNode("button")
        text_dom = DOMNode("text", text="Click Me")
        button_dom.add_child(text_dom)

        element = ButtonElement(button_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.dom_node == button_dom
        assert hasattr(layout_node, "box")
        assert hasattr(layout_node, "button_text")
        assert hasattr(layout_node, "button_padding")
        assert layout_node.button_text == "Click Me"
        assert self.layout_engine.current_y > initial_y

    def test_button_element_with_empty_content(self) -> None:
        """Test ButtonElement with empty content returns None"""
        button_dom = DOMNode("button")
        element = ButtonElement(button_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is None

    def test_button_element_with_whitespace_only(self) -> None:
        """Test ButtonElement with whitespace-only content returns None"""
        button_dom = DOMNode("button")
        text_dom = DOMNode("text", text="   ")
        button_dom.add_child(text_dom)

        element = ButtonElement(button_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is None

    def test_button_element_with_nested_content(self) -> None:
        """Test ButtonElement extracts text from nested children"""
        button_dom = DOMNode("button")
        span_dom = DOMNode("span")
        text_dom = DOMNode("text", text="Submit")

        span_dom.add_child(text_dom)
        button_dom.add_child(span_dom)

        element = ButtonElement(button_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.button_text == "Submit"

    def test_button_element_dimensions_calculation(self) -> None:
        """Test ButtonElement calculates dimensions correctly"""
        button_dom = DOMNode("button")
        text_dom = DOMNode("text", text="OK")
        button_dom.add_child(text_dom)

        element = ButtonElement(button_dom)

        layout_node = element.layout(self.layout_engine, 20, 1000)

        assert layout_node is not None

        # Expected dimensions based on text and padding
        expected_padding = self.config.PADDING * 2
        expected_char_width = self.config.CHAR_WIDTH_ESTIMATE
        expected_text_width = len("OK") * expected_char_width
        expected_width = expected_text_width + 2 * expected_padding

        font_size = self.layout_engine.DEFAULT_FONT_SIZE
        line_height = font_size * self.layout_engine.LINE_HEIGHT
        expected_height = line_height + 2 * expected_padding

        assert layout_node.box.width == expected_width
        assert layout_node.box.height == expected_height
        assert layout_node.button_padding == expected_padding

    def test_button_element_position_calculation(self) -> None:
        """Test ButtonElement positions correctly"""
        button_dom = DOMNode("button")
        text_dom = DOMNode("text", text="Test")
        button_dom.add_child(text_dom)

        element = ButtonElement(button_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 50, 800)

        assert layout_node is not None
        assert layout_node.box.x == 50
        assert layout_node.box.y == initial_y

        # Check that layout engine current_y is updated
        expected_height = layout_node.box.height
        expected_margin = self.config.MARGIN
        expected_y = initial_y + expected_height + expected_margin
        assert self.layout_engine.current_y == expected_y

    def test_button_element_render_basic(self) -> None:
        """Test basic ButtonElement rendering"""
        button_dom = DOMNode("button")
        text_dom = DOMNode("text", text="Click")
        button_dom.add_child(text_dom)

        element = ButtonElement(button_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)
        layout_node.box = Box(10, 20, 80, 30)

        mock_renderer = Mock()
        mock_font = Mock()
        mock_renderer._get_font.return_value = mock_font

        mock_draw = Mock()
        # Mock textbbox to return reasonable values
        mock_draw.textbbox.return_value = (0, 0, 40, 16)  # text width=40, height=16

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have requested default font
        mock_renderer._get_font.assert_called_once()

        # Should have drawn background rectangle
        assert mock_draw.rectangle.call_count == 1

        # Should have drawn text
        assert mock_draw.text.call_count == 1

    def test_button_element_render_styling(self) -> None:
        """Test ButtonElement renders with correct styling"""
        button_dom = DOMNode("button")
        text_dom = DOMNode("text", text="Save")
        button_dom.add_child(text_dom)

        element = ButtonElement(button_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)
        layout_node.box = Box(50, 100, 100, 40)

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()

        mock_draw = Mock()
        mock_draw.textbbox.return_value = (0, 0, 50, 20)

        element.render(mock_draw, layout_node, mock_renderer)

        # Check background rectangle was drawn with correct styling
        mock_draw.rectangle.assert_called_once()
        args, kwargs = mock_draw.rectangle.call_args

        expected_rect = (50, 100, 150, 140)  # x, y, x+width, y+height
        assert args[0] == expected_rect
        assert kwargs.get("fill") == "#f0f0f0"
        assert kwargs.get("outline") == "#999999"
        assert kwargs.get("width") == 1

        # Check text was drawn with correct styling
        mock_draw.text.assert_called_once()
        text_args, text_kwargs = mock_draw.text.call_args
        assert text_kwargs.get("fill") == "#333333"

    def test_button_element_render_text_centering(self) -> None:
        """Test ButtonElement centers text correctly"""
        button_dom = DOMNode("button")
        text_dom = DOMNode("text", text="Center")
        button_dom.add_child(text_dom)

        element = ButtonElement(button_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)
        layout_node.box = Box(0, 0, 100, 50)

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()

        mock_draw = Mock()
        # Text dimensions: width=60, height=20
        mock_draw.textbbox.return_value = (0, 0, 60, 20)

        element.render(mock_draw, layout_node, mock_renderer)

        # Check text positioning
        mock_draw.text.assert_called_once()
        text_args, text_kwargs = mock_draw.text.call_args

        # Text should be centered in button
        expected_x = 0 + (100 - 60) / 2  # x + (width - text_width) / 2 = 20
        expected_y = 0 + (50 - 20) / 2  # y + (height - text_height) / 2 = 15

        assert text_args[0] == (expected_x, expected_y)
        assert text_args[1] == "Center"

    def test_button_element_render_empty_layout_node(self) -> None:
        """Test ButtonElement handles empty layout node gracefully"""
        button_dom = DOMNode("button")
        element = ButtonElement(button_dom)

        layout_node = Mock(spec=["box"])
        layout_node.box = Box(10, 20, 100, 50)
        # No button_text attribute

        mock_renderer = Mock()
        mock_draw = Mock()

        # Should not crash with missing button_text
        element.render(mock_draw, layout_node, mock_renderer)

        # Should not have drawn anything
        mock_draw.rectangle.assert_not_called()
        mock_draw.text.assert_not_called()

    def test_button_element_multiple_text_nodes(self) -> None:
        """Test ButtonElement combines multiple text nodes"""
        button_dom = DOMNode("button")
        text1_dom = DOMNode("text", text="Save ")
        text2_dom = DOMNode("text", text="File")
        button_dom.add_child(text1_dom)
        button_dom.add_child(text2_dom)

        element = ButtonElement(button_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.button_text == "Save File"

    def test_get_button_text_recursive(self) -> None:
        """Test _get_button_text extracts text recursively"""
        button_dom = DOMNode("button")

        # Create nested structure: button > strong > text
        strong_dom = DOMNode("strong")
        nested_text = DOMNode("text", text="Bold Button")
        strong_dom.add_child(nested_text)
        button_dom.add_child(strong_dom)

        element = ButtonElement(button_dom)

        result = element._get_button_text()
        assert result == "Bold Button"

    def test_get_button_text_with_none_text(self) -> None:
        """Test _get_button_text handles None text gracefully"""
        button_dom = DOMNode("button")
        text_dom = DOMNode("text", text=None)
        button_dom.add_child(text_dom)

        element = ButtonElement(button_dom)

        result = element._get_button_text()
        assert result == ""

    def test_get_button_text_with_whitespace(self) -> None:
        """Test _get_button_text strips whitespace"""
        button_dom = DOMNode("button")
        text_dom = DOMNode("text", text="  Button Text  ")
        button_dom.add_child(text_dom)

        element = ButtonElement(button_dom)

        result = element._get_button_text()
        assert result == "Button Text"

    def test_button_element_layout_engine_updates(self) -> None:
        """Test ButtonElement properly updates layout engine state"""
        button_dom = DOMNode("button")
        text_dom = DOMNode("text", text="Update Test")
        button_dom.add_child(text_dom)

        element = ButtonElement(button_dom)

        # Record initial state
        initial_y = self.layout_engine.current_y

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        # current_y should have increased by button height + margin
        expected_increase = layout_node.box.height + self.config.MARGIN
        assert self.layout_engine.current_y == initial_y + expected_increase

    def test_button_element_width_constraint(self) -> None:
        """Test ButtonElement respects viewport width constraints"""
        button_dom = DOMNode("button")
        # Very long text that might exceed viewport width
        long_text = "This is a very long button text that might exceed viewport"
        text_dom = DOMNode("text", text=long_text)
        button_dom.add_child(text_dom)

        element = ButtonElement(button_dom)

        layout_node = element.layout(self.layout_engine, 10, 200)  # Small viewport

        assert layout_node is not None
        # Button should be created regardless (no text wrapping for now)
        assert layout_node.button_text == long_text
        # Width is based on text estimation, not constrained to viewport
        assert layout_node.box.width > 0

    def test_button_element_consistent_creation(self) -> None:
        """Test ButtonElement creates consistent results"""
        button_dom = DOMNode("button")
        text_dom = DOMNode("text", text="Consistent")
        button_dom.add_child(text_dom)

        element1 = ButtonElement(button_dom)
        element2 = ButtonElement(button_dom)

        layout1 = element1.layout(self.layout_engine, 10, 800)
        # Reset layout engine for second test
        self.layout_engine.current_y = 0
        layout2 = element2.layout(self.layout_engine, 10, 800)

        assert layout1 is not None
        assert layout2 is not None
        assert layout1.button_text == layout2.button_text
        assert layout1.box.width == layout2.box.width
        assert layout1.box.height == layout2.box.height
