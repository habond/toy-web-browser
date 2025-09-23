"""
Unit tests for select and option elements
"""

from unittest.mock import MagicMock, Mock, patch

from src.elements.select import OptionElement, SelectElement
from src.html_parser import DOMNode


class TestOptionElement:
    """Test suite for OptionElement"""

    def test_layout_returns_none(self) -> None:
        """Option elements should not have their own layout"""
        dom_node = DOMNode("option", {}, None)
        option = OptionElement(dom_node)
        layout_engine = Mock()

        result = option.layout(layout_engine, 0, 800)

        assert result is None

    def test_get_text_extracts_content(self) -> None:
        """Should extract text content from option"""
        text_node = DOMNode("text", {}, "Option Text")
        dom_node = DOMNode("option", {}, None)
        dom_node.children = [text_node]
        option = OptionElement(dom_node)

        text = option.get_text()

        assert text == "Option Text"

    def test_get_value_returns_attribute(self) -> None:
        """Should return value attribute if present"""
        text_node = DOMNode("text", {}, "Display Text")
        dom_node = DOMNode("option", {"value": "opt1"}, None)
        dom_node.children = [text_node]
        option = OptionElement(dom_node)

        value = option.get_value()

        assert value == "opt1"

    def test_get_value_returns_text_if_no_attribute(self) -> None:
        """Should return text content if no value attribute"""
        text_node = DOMNode("text", {}, "Option Text")
        dom_node = DOMNode("option", {}, None)
        dom_node.children = [text_node]
        option = OptionElement(dom_node)

        value = option.get_value()

        assert value == "Option Text"

    def test_is_selected_checks_attribute(self) -> None:
        """Should check for selected attribute"""
        # Selected option
        dom_node_selected = DOMNode("option", {"selected": ""}, None)
        dom_node_selected.children = []
        option_selected = OptionElement(dom_node_selected)

        # Unselected option
        dom_node_unselected = DOMNode("option", {}, None)
        dom_node_unselected.children = []
        option_unselected = OptionElement(dom_node_unselected)

        assert option_selected.is_selected() is True
        assert option_unselected.is_selected() is False


class TestSelectElement:
    """Test suite for SelectElement"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.layout_engine = Mock()
        self.layout_engine.current_y = 100
        self.layout_engine.DEFAULT_FONT_SIZE = 16
        self.layout_engine.LINE_HEIGHT = 1.5

    def test_layout_with_selected_option(self) -> None:
        """Should layout select with selected option text"""
        # Create option nodes
        option1_text = DOMNode("text", {}, "Option 1")
        option1 = DOMNode("option", {}, None)
        option1.children = [option1_text]

        option2_text = DOMNode("text", {}, "Option 2")
        option2 = DOMNode("option", {"selected": ""}, None)
        option2.children = [option2_text]

        dom_node = DOMNode("select", {}, None)
        dom_node.children = [option1, option2]
        select = SelectElement(dom_node)

        layout_node = select.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert getattr(layout_node, "selected_text", None) == "Option 2"
        assert getattr(layout_node, "display_text", None) == "Option 2"
        assert hasattr(layout_node, "options")
        options = getattr(layout_node, "options", [])
        assert len(options) == 2

    def test_layout_with_no_selected_option(self) -> None:
        """Should default to first option if none selected"""
        # Create option nodes
        option1_text = DOMNode("text", {}, "First Option")
        option1 = DOMNode("option", {}, None)
        option1.children = [option1_text]

        option2_text = DOMNode("text", {}, "Second Option")
        option2 = DOMNode("option", {}, None)
        option2.children = [option2_text]

        dom_node = DOMNode("select", {}, None)
        dom_node.children = [option1, option2]
        select = SelectElement(dom_node)

        layout_node = select.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert getattr(layout_node, "selected_text", None) == "First Option"
        assert getattr(layout_node, "display_text", None) == "First Option"

    def test_layout_with_no_options(self) -> None:
        """Should show placeholder when no options"""
        dom_node = DOMNode("select", {}, None)
        dom_node.children = []
        select = SelectElement(dom_node)

        layout_node = select.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert getattr(layout_node, "selected_text", None) is None
        assert getattr(layout_node, "display_text", None) == "Select..."

    def test_layout_updates_current_y(self) -> None:
        """Should update layout engine's current_y after layout"""
        dom_node = DOMNode("select", {}, None)
        dom_node.children = []
        select = SelectElement(dom_node)
        initial_y = self.layout_engine.current_y

        select.layout(self.layout_engine, 10, 800)

        assert self.layout_engine.current_y > initial_y

    @patch("src.elements.select.ImageDraw")
    def test_render_with_selected_text(self, mock_draw_class: MagicMock) -> None:
        """Should render select box with selected text"""
        mock_draw = Mock()
        renderer = Mock()
        renderer._get_font.return_value = Mock()

        layout_node = Mock()
        layout_node.display_text = "Selected Option"
        layout_node.selected_text = "Selected Option"
        layout_node.padding = 10
        layout_node.box = Mock()
        layout_node.box.x = 10
        layout_node.box.y = 20
        layout_node.box.width = 200
        layout_node.box.height = 40

        dom_node = DOMNode("select", {}, None)
        dom_node.children = []
        select = SelectElement(dom_node)

        select.render(mock_draw, layout_node, renderer)

        # Should draw rectangle for select box
        mock_draw.rectangle.assert_called_once()
        # Should draw text for selected option
        mock_draw.text.assert_called()
        # Should draw dropdown arrow
        mock_draw.polygon.assert_called_once()

    @patch("src.elements.select.ImageDraw")
    def test_render_without_selected_text(self, mock_draw_class: MagicMock) -> None:
        """Should render placeholder with gray text when no selection"""
        mock_draw = Mock()
        renderer = Mock()
        renderer._get_font.return_value = Mock()

        layout_node = Mock()
        layout_node.display_text = "Select..."
        layout_node.selected_text = None
        layout_node.padding = 10
        layout_node.box = Mock()
        layout_node.box.x = 10
        layout_node.box.y = 20
        layout_node.box.width = 200
        layout_node.box.height = 40

        dom_node = DOMNode("select", {}, None)
        dom_node.children = []
        select = SelectElement(dom_node)

        select.render(mock_draw, layout_node, renderer)

        # Should use gray color for placeholder text
        text_calls = mock_draw.text.call_args_list
        assert len(text_calls) > 0
        # Check that gray color (#999999) was used
        assert text_calls[0][1]["fill"] == "#999999"
