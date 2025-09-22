"""Tests for the InputElement class"""

from unittest.mock import Mock

from src.config import BrowserConfig
from src.elements.input import InputElement
from src.html_parser import DOMNode
from src.layout_engine import LayoutEngine
from tests.fixtures.test_utils import MockFactory


class TestInputElement:
    """Test the InputElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.mock_font_manager = MockFactory.create_font_manager_mock()
        self.layout_engine = LayoutEngine()

    def test_input_element_creation(self) -> None:
        """Test InputElement can be created"""
        dom_node = DOMNode("input")
        element = InputElement(dom_node)

        assert element is not None
        assert element.dom_node == dom_node

    def test_text_input_layout(self) -> None:
        """Test text input layout"""
        dom_node = DOMNode("input", {"type": "text", "value": "test"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.box.x == 10
        assert layout_node.box.width == 200.0  # Fixed width for text inputs
        expected_height = self.config.DEFAULT_FONT_SIZE + 2 * self.config.PADDING
        assert layout_node.box.height == expected_height
        assert getattr(layout_node, "display_text", None) == "test"
        assert getattr(layout_node, "input_type", None) == "text"
        assert getattr(layout_node, "is_placeholder", None) is False

    def test_text_input_with_placeholder(self) -> None:
        """Test text input with placeholder"""
        dom_node = DOMNode("input", {"type": "text", "placeholder": "Enter text"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)

        assert layout_node is not None
        assert getattr(layout_node, "display_text", None) == "Enter text"
        assert getattr(layout_node, "is_placeholder", None) is True

    def test_button_input_layout(self) -> None:
        """Test button input layout"""
        dom_node = DOMNode("input", {"type": "submit", "value": "Submit"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)

        assert layout_node is not None
        # Width should be based on text length
        text_width = len("Submit") * self.config.CHAR_WIDTH_ESTIMATE
        expected_width = text_width + 2 * self.config.PADDING + 20
        assert layout_node.box.width == expected_width
        assert getattr(layout_node, "display_text", None) == "Submit"
        assert getattr(layout_node, "input_type", None) == "submit"

    def test_button_input_default_text(self) -> None:
        """Test button input with default text"""
        dom_node = DOMNode("input", {"type": "submit"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)

        assert layout_node is not None
        assert getattr(layout_node, "display_text", None) == "Submit"

    def test_checkbox_layout(self) -> None:
        """Test checkbox input layout"""
        dom_node = DOMNode("input", {"type": "checkbox"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)

        assert layout_node is not None
        assert layout_node.box.width == 16.0
        assert layout_node.box.height == 16.0
        assert getattr(layout_node, "input_type", None) == "checkbox"

    def test_radio_layout(self) -> None:
        """Test radio input layout"""
        dom_node = DOMNode("input", {"type": "radio"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)

        assert layout_node is not None
        assert layout_node.box.width == 16.0
        assert layout_node.box.height == 16.0
        assert getattr(layout_node, "input_type", None) == "radio"

    def test_email_input_layout(self) -> None:
        """Test email input layout"""
        dom_node = DOMNode("input", {"type": "email", "value": "test@example.com"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)

        assert layout_node is not None
        assert layout_node.box.width == 200.0  # Same as text input
        assert getattr(layout_node, "display_text", None) == "test@example.com"
        assert getattr(layout_node, "input_type", None) == "email"

    def test_password_input_layout(self) -> None:
        """Test password input layout"""
        dom_node = DOMNode("input", {"type": "password", "value": "secret"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)

        assert layout_node is not None
        assert layout_node.box.width == 200.0
        assert getattr(layout_node, "display_text", None) == "secret"
        assert getattr(layout_node, "input_type", None) == "password"

    def test_unknown_input_type_defaults_to_text(self) -> None:
        """Test unknown input type defaults to text behavior"""
        dom_node = DOMNode("input", {"type": "unknown", "value": "test"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)

        assert layout_node is not None
        assert layout_node.box.width == 100.0  # Default width
        assert getattr(layout_node, "input_type", None) == "unknown"

    def test_render_text_input(self) -> None:
        """Test rendering text input"""
        dom_node = DOMNode("input", {"type": "text", "value": "test"})
        element = InputElement(dom_node)

        # Create layout node
        layout_node = element.layout(self.layout_engine, 0, 800)
        assert layout_node is not None

        # Mock objects for rendering
        mock_draw = Mock()
        mock_draw.textlength.return_value = 30  # Mock text width (small enough to fit)
        mock_renderer = Mock()
        mock_renderer.font_manager = self.mock_font_manager

        # Call render method
        element.render(mock_draw, layout_node, mock_renderer)

        # Verify rectangle and text drawing calls
        mock_draw.rectangle.assert_called_once()
        mock_draw.text.assert_called_once()

    def test_render_button_input(self) -> None:
        """Test rendering button input"""
        dom_node = DOMNode("input", {"type": "submit", "value": "Submit"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)
        assert layout_node is not None

        mock_draw = Mock()
        mock_draw.textlength.return_value = 50  # Mock text width
        mock_renderer = Mock()
        mock_renderer.font_manager = self.mock_font_manager

        element.render(mock_draw, layout_node, mock_renderer)

        # Verify button rendering
        mock_draw.rectangle.assert_called_once()
        mock_draw.text.assert_called_once()

    def test_render_checkbox_unchecked(self) -> None:
        """Test rendering unchecked checkbox"""
        dom_node = DOMNode("input", {"type": "checkbox"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)
        assert layout_node is not None

        mock_draw = Mock()
        mock_renderer = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Verify checkbox rectangle drawn but no checkmark
        mock_draw.rectangle.assert_called_once()
        mock_draw.line.assert_not_called()

    def test_render_checkbox_checked(self) -> None:
        """Test rendering checked checkbox"""
        dom_node = DOMNode("input", {"type": "checkbox", "checked": ""})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)
        assert layout_node is not None

        mock_draw = Mock()
        mock_renderer = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Verify checkbox rectangle and checkmark lines drawn
        mock_draw.rectangle.assert_called_once()
        assert mock_draw.line.call_count == 2  # Two lines for checkmark

    def test_render_radio_unchecked(self) -> None:
        """Test rendering unchecked radio button"""
        dom_node = DOMNode("input", {"type": "radio"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)
        assert layout_node is not None

        mock_draw = Mock()
        mock_renderer = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Verify radio circle drawn but no filled center
        assert mock_draw.ellipse.call_count == 1

    def test_render_radio_checked(self) -> None:
        """Test rendering checked radio button"""
        dom_node = DOMNode("input", {"type": "radio", "checked": ""})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)
        assert layout_node is not None

        mock_draw = Mock()
        mock_renderer = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Verify radio circle and filled center drawn
        assert mock_draw.ellipse.call_count == 2  # Outer circle and inner filled circle

    def test_render_placeholder_text_styling(self) -> None:
        """Test placeholder text is rendered with gray color"""
        dom_node = DOMNode("input", {"type": "text", "placeholder": "Enter text"})
        element = InputElement(dom_node)

        layout_node = element.layout(self.layout_engine, 0, 800)
        assert layout_node is not None

        mock_draw = Mock()
        mock_draw.textlength.return_value = 50  # Mock text width
        mock_renderer = Mock()
        mock_renderer.font_manager = self.mock_font_manager

        element.render(mock_draw, layout_node, mock_renderer)

        # Verify text is rendered with gray color for placeholder
        text_call = mock_draw.text.call_args
        assert text_call[1]["fill"] == "#888888"  # Gray color for placeholder
