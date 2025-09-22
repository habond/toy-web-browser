"""Tests for the PreElement class"""

from unittest.mock import Mock

from src.config import BrowserConfig
from src.elements.pre import PreElement
from src.html_parser import DOMNode
from src.layout_engine import Box, LayoutEngine
from tests.fixtures.test_utils import MockFactory


class TestPreElement:
    """Test the PreElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.mock_font_manager = MockFactory.create_font_manager_mock()
        self.layout_engine = LayoutEngine()

    def test_pre_element_creation(self) -> None:
        """Test PreElement can be created"""
        dom_node = DOMNode("pre")
        element = PreElement(dom_node)

        assert element is not None
        assert element.dom_node == dom_node

    def test_pre_element_with_simple_text(self) -> None:
        """Test PreElement with simple text content"""
        pre_dom = DOMNode("pre")
        text_dom = DOMNode("text", text="Hello World")
        pre_dom.add_child(text_dom)

        element = PreElement(pre_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.dom_node == pre_dom
        assert hasattr(layout_node, "box")
        assert hasattr(layout_node, "lines")
        assert hasattr(layout_node, "font_type")
        assert layout_node.font_type == "monospace"
        assert layout_node.lines == ["Hello World"]
        assert self.layout_engine.current_y > initial_y

    def test_pre_element_with_multiline_text(self) -> None:
        """Test PreElement preserves multiple lines"""
        pre_dom = DOMNode("pre")
        text_dom = DOMNode("text", text="Line 1\nLine 2\nLine 3")
        pre_dom.add_child(text_dom)

        element = PreElement(pre_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.lines == ["Line 1", "Line 2", "Line 3"]

    def test_pre_element_preserves_whitespace(self) -> None:
        """Test PreElement preserves leading and trailing whitespace"""
        pre_dom = DOMNode("pre")
        text_dom = DOMNode("text", text="  indented line  \n    more indented    ")
        pre_dom.add_child(text_dom)

        element = PreElement(pre_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.lines == ["  indented line  ", "    more indented    "]

    def test_pre_element_preserves_empty_lines(self) -> None:
        """Test PreElement preserves empty lines"""
        pre_dom = DOMNode("pre")
        text_dom = DOMNode("text", text="Line 1\n\nLine 3\n\n\nLine 6")
        pre_dom.add_child(text_dom)

        element = PreElement(pre_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.lines == ["Line 1", "", "Line 3", "", "", "Line 6"]

    def test_pre_element_with_nested_children(self) -> None:
        """Test PreElement extracts text from nested children"""
        pre_dom = DOMNode("pre")
        text1_dom = DOMNode("text", text="First ")
        code_dom = DOMNode("code")
        text2_dom = DOMNode("text", text="code")
        text3_dom = DOMNode("text", text=" last")

        code_dom.add_child(text2_dom)
        pre_dom.add_child(text1_dom)
        pre_dom.add_child(code_dom)
        pre_dom.add_child(text3_dom)

        element = PreElement(pre_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.lines == ["First code last"]

    def test_pre_element_with_empty_content(self) -> None:
        """Test PreElement with empty content returns None"""
        pre_dom = DOMNode("pre")
        element = PreElement(pre_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is None

    def test_pre_element_with_whitespace_only(self) -> None:
        """Test PreElement with whitespace-only content"""
        pre_dom = DOMNode("pre")
        text_dom = DOMNode("text", text="   \n   \n   ")
        pre_dom.add_child(text_dom)

        element = PreElement(pre_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.lines == ["   ", "   ", "   "]

    def test_pre_element_height_calculation(self) -> None:
        """Test PreElement calculates height correctly based on line count"""
        pre_dom = DOMNode("pre")
        text_dom = DOMNode("text", text="Line 1\nLine 2\nLine 3")
        pre_dom.add_child(text_dom)

        element = PreElement(pre_dom)

        initial_y = self.layout_engine.current_y
        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None

        # Height should be: num_lines * line_height + 2 * margin
        font_size = self.layout_engine.DEFAULT_FONT_SIZE
        line_height_mult = self.layout_engine.LINE_HEIGHT
        expected_line_height = font_size * line_height_mult
        expected_margin = self.layout_engine.MARGIN
        expected_height = 3 * expected_line_height + 2 * expected_margin

        assert layout_node.box.height == expected_height
        assert self.layout_engine.current_y == initial_y + expected_height

    def test_pre_element_width_calculation(self) -> None:
        """Test PreElement width calculation"""
        pre_dom = DOMNode("pre")
        text_dom = DOMNode("text", text="Some text")
        pre_dom.add_child(text_dom)

        element = PreElement(pre_dom)

        layout_node = element.layout(self.layout_engine, 20, 1000)

        assert layout_node is not None
        expected_width = 1000 - 2 * 20  # viewport_width - 2 * x
        assert layout_node.box.width == expected_width

    def test_pre_element_render_basic(self) -> None:
        """Test basic PreElement rendering"""
        pre_dom = DOMNode("pre")
        text_dom = DOMNode("text", text="Hello\nWorld")
        pre_dom.add_child(text_dom)

        element = PreElement(pre_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)
        layout_node.box = Box(10, 20, 400, 100)

        mock_renderer = Mock()
        mock_font = Mock()
        mock_renderer._get_font.return_value = mock_font
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have requested monospace font
        mock_renderer._get_font.assert_called_once_with(monospace=True)

        # Should have drawn background rectangle
        assert mock_draw.rectangle.call_count == 1

        # Should have drawn text for each line
        assert mock_draw.text.call_count == 2

    def test_pre_element_render_with_background(self) -> None:
        """Test PreElement renders background correctly"""
        pre_dom = DOMNode("pre")
        text_dom = DOMNode("text", text="Code")
        pre_dom.add_child(text_dom)

        element = PreElement(pre_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)
        layout_node.box = Box(50, 100, 400, 200)

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Check background rectangle was drawn
        mock_draw.rectangle.assert_called_once()

        # Verify background coordinates
        args, kwargs = mock_draw.rectangle.call_args
        coords = args[0]

        expected_padding = self.config.PADDING
        expected_coords = (
            50 - expected_padding,  # x - padding
            100,  # y
            50 + 400,  # x + width
            100 + 200,  # y + height (no margin subtraction)
        )

        assert coords == expected_coords
        assert kwargs.get("fill") == "#f8f8f8"
        assert kwargs.get("outline") == "#e0e0e0"

    def test_pre_element_render_text_positioning(self) -> None:
        """Test PreElement positions text correctly"""
        pre_dom = DOMNode("pre")
        text_dom = DOMNode("text", text="Line 1\nLine 2")
        pre_dom.add_child(text_dom)

        element = PreElement(pre_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)
        layout_node.box = Box(50, 100, 400, 200)

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have called text method twice
        assert mock_draw.text.call_count == 2

        # Check first line positioning
        first_call = mock_draw.text.call_args_list[0]
        first_pos = first_call[0][0]
        first_text = first_call[0][1]

        expected_padding = self.config.PADDING
        expected_margin = self.config.MARGIN
        expected_x = 50 + expected_padding
        expected_y = 100 + expected_margin

        assert first_pos == (expected_x, expected_y)
        assert first_text == "Line 1"

        # Check second line positioning
        second_call = mock_draw.text.call_args_list[1]
        second_pos = second_call[0][0]
        second_text = second_call[0][1]

        line_height = 16 * 1.5
        expected_y_second = expected_y + line_height

        assert second_pos == (expected_x, expected_y_second)
        assert second_text == "Line 2"

    def test_pre_element_render_empty_layout_node(self) -> None:
        """Test PreElement handles empty layout node gracefully"""
        pre_dom = DOMNode("pre")
        element = PreElement(pre_dom)

        layout_node = Mock(spec=["box"])
        layout_node.box = Box(10, 20, 100, 50)

        mock_renderer = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5
        mock_draw = Mock()

        # Should not crash with missing lines
        element.render(mock_draw, layout_node, mock_renderer)

        # Should not have drawn anything
        mock_draw.rectangle.assert_not_called()
        mock_draw.text.assert_not_called()

    def test_pre_element_render_with_empty_lines(self) -> None:
        """Test PreElement renders empty lines correctly"""
        pre_dom = DOMNode("pre")
        text_dom = DOMNode("text", text="Line 1\n\nLine 3")
        pre_dom.add_child(text_dom)

        element = PreElement(pre_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have called text method 3 times (including empty line)
        assert mock_draw.text.call_count == 3

        # Check that empty line is rendered (even if it's empty string)
        second_call = mock_draw.text.call_args_list[1]
        second_text = second_call[0][1]
        assert second_text == ""

    def test_get_preformatted_text_recursive(self) -> None:
        """Test _get_preformatted_text extracts text recursively"""
        pre_dom = DOMNode("pre")

        # Create nested structure: pre > span > text
        span_dom = DOMNode("span")
        nested_text = DOMNode("text", text="nested")
        span_dom.add_child(nested_text)

        text1_dom = DOMNode("text", text="before ")
        text2_dom = DOMNode("text", text=" after")

        pre_dom.add_child(text1_dom)
        pre_dom.add_child(span_dom)
        pre_dom.add_child(text2_dom)

        element = PreElement(pre_dom)

        result = element._get_preformatted_text()
        assert result == "before nested after"

    def test_get_preformatted_text_with_none_text(self) -> None:
        """Test _get_preformatted_text handles None text gracefully"""
        pre_dom = DOMNode("pre")
        text_dom = DOMNode("text", text=None)
        pre_dom.add_child(text_dom)

        element = PreElement(pre_dom)

        result = element._get_preformatted_text()
        assert result == ""
