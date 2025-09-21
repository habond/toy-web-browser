"""Tests for the InlineElement class"""

from unittest.mock import Mock, patch

import pytest

from src.config import BrowserConfig
from src.elements.inline import InlineElement
from src.html_parser import DOMNode
from src.layout_engine import LayoutEngine, LayoutNode
from tests.fixtures.test_utils import MockFactory, TestDataBuilder


class TestInlineElement:
    """Test the InlineElement class"""

    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.config = BrowserConfig()
        self.layout_engine = LayoutEngine()

    def test_inline_element_creation(self) -> None:
        """Test InlineElement can be created"""
        dom_node = DOMNode("b")
        element = InlineElement(dom_node)

        assert element is not None
        assert element.dom_node == dom_node

    def test_inline_element_supported_tags(self) -> None:
        """Test InlineElement works with all supported inline tags"""
        inline_tags = ["b", "i", "u", "strong", "em", "code", "span", "a"]

        for tag in inline_tags:
            dom_node = DOMNode(tag)
            element = InlineElement(dom_node)

            assert element is not None
            assert element.dom_node.tag == tag

    def test_inline_element_basic_layout(self) -> None:
        """Test basic inline element layout"""
        b_dom = DOMNode("b")
        text_dom = DOMNode("text", text="Bold text")
        b_dom.add_child(text_dom)

        element = InlineElement(b_dom)

        # Mock child layout
        mock_child_layout = Mock()
        self.layout_engine._layout_child = Mock(return_value=mock_child_layout)

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert layout_node.dom_node == b_dom
        assert len(layout_node.children) == 1
        assert layout_node.children[0] == mock_child_layout

        # Should have called _layout_child
        self.layout_engine._layout_child.assert_called_with(text_dom, 10)

    def test_inline_element_no_children(self) -> None:
        """Test inline element with no children"""
        span_dom = DOMNode("span")
        element = InlineElement(span_dom)

        layout_node = element.layout(self.layout_engine, 10, 800)

        # Should return None when no children
        assert layout_node is None

    def test_inline_element_children_return_none(self) -> None:
        """Test inline element when children layout returns None"""
        i_dom = DOMNode("i")
        text_dom = DOMNode("text", text="")  # Empty text might return None
        i_dom.add_child(text_dom)

        element = InlineElement(i_dom)

        # Mock child layout returning None
        self.layout_engine._layout_child = Mock(return_value=None)

        layout_node = element.layout(self.layout_engine, 10, 800)

        # Should return None when no valid children
        assert layout_node is None

    def test_inline_element_multiple_children(self) -> None:
        """Test inline element with multiple children"""
        strong_dom = DOMNode("strong")
        text1_dom = DOMNode("text", text="Strong ")
        text2_dom = DOMNode("text", text="text")
        strong_dom.add_child(text1_dom)
        strong_dom.add_child(text2_dom)

        element = InlineElement(strong_dom)

        mock_child1 = Mock()
        mock_child2 = Mock()
        self.layout_engine._layout_child = Mock(side_effect=[mock_child1, mock_child2])

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert len(layout_node.children) == 2
        assert layout_node.children[0] == mock_child1
        assert layout_node.children[1] == mock_child2

    def test_inline_element_mixed_children(self) -> None:
        """Test inline element with mix of valid and None children"""
        span_dom = DOMNode("span")
        text1_dom = DOMNode("text", text="Valid")
        text2_dom = DOMNode("text", text="")  # Might return None
        span_dom.add_child(text1_dom)
        span_dom.add_child(text2_dom)

        element = InlineElement(span_dom)

        mock_child1 = Mock()
        self.layout_engine._layout_child = Mock(side_effect=[mock_child1, None])

        layout_node = element.layout(self.layout_engine, 10, 800)

        assert layout_node is not None
        assert len(layout_node.children) == 1  # Only valid child
        assert layout_node.children[0] == mock_child1

    def test_inline_element_render_bold_text(self) -> None:
        """Test rendering bold inline element"""
        b_dom = DOMNode("b")
        element = InlineElement(b_dom)

        # Create mock text child
        mock_text_child = Mock()
        mock_text_child.dom_node = Mock()
        mock_text_child.dom_node.tag = "text"
        mock_text_child.lines = ["Bold text"]
        mock_text_child.box = Mock()
        mock_text_child.box.x = 10
        mock_text_child.box.y = 20

        layout_node = LayoutNode(b_dom)
        layout_node.children = [mock_text_child]

        mock_font = Mock()
        mock_renderer = Mock()
        mock_renderer._get_font.return_value = mock_font
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have requested bold font
        mock_renderer._get_font.assert_called_with(
            bold=True, italic=False, monospace=False
        )

        # Should have drawn text
        mock_draw.text.assert_called()
        args, kwargs = mock_draw.text.call_args
        assert kwargs.get("fill") == "black"
        assert kwargs.get("font") == mock_font

    def test_inline_element_render_italic_text(self) -> None:
        """Test rendering italic inline element"""
        i_dom = DOMNode("i")
        element = InlineElement(i_dom)

        mock_text_child = Mock()
        mock_text_child.dom_node = Mock()
        mock_text_child.dom_node.tag = "text"
        mock_text_child.lines = ["Italic text"]
        mock_text_child.box = Mock()
        mock_text_child.box.x = 10
        mock_text_child.box.y = 20

        layout_node = LayoutNode(i_dom)
        layout_node.children = [mock_text_child]

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have requested italic font
        mock_renderer._get_font.assert_called_with(
            bold=False, italic=True, monospace=False
        )

    def test_inline_element_render_underline_text(self) -> None:
        """Test rendering underlined inline element"""
        u_dom = DOMNode("u")
        element = InlineElement(u_dom)

        mock_text_child = Mock()
        mock_text_child.dom_node = Mock()
        mock_text_child.dom_node.tag = "text"
        mock_text_child.lines = ["Underlined text"]
        mock_text_child.box = Mock()
        mock_text_child.box.x = 10
        mock_text_child.box.y = 20

        layout_node = LayoutNode(u_dom)
        layout_node.children = [mock_text_child]

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()
        mock_draw.textlength.return_value = 100  # Mock text width

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have drawn underline
        mock_draw.line.assert_called()
        line_args = mock_draw.line.call_args[0][0]
        # Should draw line from text start to text end
        assert line_args[0] == 10  # Start x
        assert line_args[2] == 110  # End x (start + width)

    def test_inline_element_render_code_text(self) -> None:
        """Test rendering code inline element with background"""
        code_dom = DOMNode("code")
        element = InlineElement(code_dom)

        mock_text_child = Mock()
        mock_text_child.dom_node = Mock()
        mock_text_child.dom_node.tag = "text"
        mock_text_child.lines = ["code_snippet"]
        mock_text_child.box = Mock()
        mock_text_child.box.x = 10
        mock_text_child.box.y = 20

        layout_node = LayoutNode(code_dom)
        layout_node.children = [mock_text_child]

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()
        mock_draw.textlength.return_value = 80

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have requested monospace font
        mock_renderer._get_font.assert_called_with(
            bold=False, italic=False, monospace=True
        )

        # Should have drawn background rectangle
        mock_draw.rectangle.assert_called()
        rect_args = mock_draw.rectangle.call_args[0][0]
        # Rectangle should surround text with padding
        assert rect_args[0] == 8  # x - padding
        assert rect_args[1] == 18  # y - padding
        assert rect_args[2] == 92  # x + width + padding
        assert rect_args[3] == 38  # y + font_size + padding

    def test_inline_element_render_link_text(self) -> None:
        """Test rendering link inline element"""
        a_dom = DOMNode("a", attrs={"href": "https://example.com"})
        element = InlineElement(a_dom)

        mock_text_child = Mock()
        mock_text_child.dom_node = Mock()
        mock_text_child.dom_node.tag = "text"
        mock_text_child.lines = ["Link text"]
        mock_text_child.box = Mock()
        mock_text_child.box.x = 10
        mock_text_child.box.y = 20

        layout_node = LayoutNode(a_dom)
        layout_node.children = [mock_text_child]

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()
        mock_draw.textlength.return_value = 70

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have drawn text in blue color
        text_args = mock_draw.text.call_args
        assert text_args[1]["fill"] == "#0066cc"

        # Should have drawn underline for link
        mock_draw.line.assert_called()

    def test_inline_element_render_strong_em_tags(self) -> None:
        """Test that strong and em tags work like b and i"""
        # Test strong (should be bold)
        strong_dom = DOMNode("strong")
        strong_element = InlineElement(strong_dom)

        mock_text_child = Mock()
        mock_text_child.dom_node = Mock()
        mock_text_child.dom_node.tag = "text"
        mock_text_child.lines = ["Strong text"]
        mock_text_child.box = Mock()
        mock_text_child.box.x = 10
        mock_text_child.box.y = 20

        layout_node = LayoutNode(strong_dom)
        layout_node.children = [mock_text_child]

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        strong_element.render(mock_draw, layout_node, mock_renderer)

        # Should have requested bold font
        mock_renderer._get_font.assert_called_with(
            bold=True, italic=False, monospace=False
        )

        # Test em (should be italic)
        em_dom = DOMNode("em")
        em_element = InlineElement(em_dom)
        layout_node.dom_node = em_dom

        mock_renderer.reset_mock()
        em_element.render(mock_draw, layout_node, mock_renderer)

        # Should have requested italic font
        mock_renderer._get_font.assert_called_with(
            bold=False, italic=True, monospace=False
        )

    def test_inline_element_render_non_text_children(self) -> None:
        """Test rendering inline element with non-text children"""
        span_dom = DOMNode("span")
        element = InlineElement(span_dom)

        # Non-text child
        mock_div_child = Mock()
        mock_div_child.dom_node = Mock()
        mock_div_child.dom_node.tag = "div"

        layout_node = LayoutNode(span_dom)
        layout_node.children = [mock_div_child]

        mock_renderer = Mock()
        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should delegate to renderer for non-text children
        mock_renderer._render_node.assert_called_with(mock_draw, mock_div_child)

    def test_inline_element_render_empty_lines(self) -> None:
        """Test rendering inline element with empty lines"""
        b_dom = DOMNode("b")
        element = InlineElement(b_dom)

        mock_text_child = Mock()
        mock_text_child.dom_node = Mock()
        mock_text_child.dom_node.tag = "text"
        mock_text_child.lines = ["Text", "", "More text"]  # Empty line in middle
        mock_text_child.box = Mock()
        mock_text_child.box.x = 10
        mock_text_child.box.y = 20

        layout_node = LayoutNode(b_dom)
        layout_node.children = [mock_text_child]

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should skip empty lines - only 2 calls for non-empty lines
        assert mock_draw.text.call_count == 2

    def test_inline_element_render_no_lines(self) -> None:
        """Test rendering inline element when child has no lines"""
        span_dom = DOMNode("span")
        element = InlineElement(span_dom)

        mock_text_child = Mock()
        mock_text_child.dom_node = Mock()
        mock_text_child.dom_node.tag = "text"
        mock_text_child.lines = None  # No lines

        layout_node = LayoutNode(span_dom)
        layout_node.children = [mock_text_child]

        mock_renderer = Mock()
        mock_draw = Mock()

        # Should not crash
        element.render(mock_draw, layout_node, mock_renderer)

    def test_inline_element_render_mixed_styling(self) -> None:
        """Test that styling detection works correctly for each tag"""
        test_cases = [
            (
                "b",
                {
                    "bold": True,
                    "italic": False,
                    "underline": False,
                    "monospace": False,
                    "is_link": False,
                },
            ),
            (
                "i",
                {
                    "bold": False,
                    "italic": True,
                    "underline": False,
                    "monospace": False,
                    "is_link": False,
                },
            ),
            (
                "u",
                {
                    "bold": False,
                    "italic": False,
                    "underline": True,
                    "monospace": False,
                    "is_link": False,
                },
            ),
            (
                "strong",
                {
                    "bold": True,
                    "italic": False,
                    "underline": False,
                    "monospace": False,
                    "is_link": False,
                },
            ),
            (
                "em",
                {
                    "bold": False,
                    "italic": True,
                    "underline": False,
                    "monospace": False,
                    "is_link": False,
                },
            ),
            (
                "code",
                {
                    "bold": False,
                    "italic": False,
                    "underline": False,
                    "monospace": True,
                    "is_link": False,
                },
            ),
            (
                "a",
                {
                    "bold": False,
                    "italic": False,
                    "underline": False,
                    "monospace": False,
                    "is_link": True,
                },
            ),
            (
                "span",
                {
                    "bold": False,
                    "italic": False,
                    "underline": False,
                    "monospace": False,
                    "is_link": False,
                },
            ),
        ]

        for tag, expected_styling in test_cases:
            dom_node = DOMNode(tag)
            element = InlineElement(dom_node)

            mock_text_child = Mock()
            mock_text_child.dom_node = Mock()
            mock_text_child.dom_node.tag = "text"
            mock_text_child.lines = ["test"]
            mock_text_child.box = Mock()
            mock_text_child.box.x = 10
            mock_text_child.box.y = 20

            layout_node = LayoutNode(dom_node)
            layout_node.children = [mock_text_child]

            mock_renderer = Mock()
            mock_renderer._get_font.return_value = Mock()
            mock_renderer.DEFAULT_FONT_SIZE = 16
            mock_renderer.LINE_HEIGHT = 1.5

            mock_draw = Mock()
            mock_draw.textlength.return_value = 50

            element.render(mock_draw, layout_node, mock_renderer)

            # Check font request
            mock_renderer._get_font.assert_called_with(
                bold=expected_styling["bold"],
                italic=expected_styling["italic"],
                monospace=expected_styling["monospace"],
            )

            # Check color
            text_call = mock_draw.text.call_args
            expected_color = "#0066cc" if expected_styling["is_link"] else "black"
            assert text_call[1]["fill"] == expected_color

            # Reset mocks for next iteration
            mock_renderer.reset_mock()
            mock_draw.reset_mock()

    def test_inline_element_line_height_calculation(self) -> None:
        """Test that line height is calculated correctly for multi-line text"""
        b_dom = DOMNode("b")
        element = InlineElement(b_dom)

        mock_text_child = Mock()
        mock_text_child.dom_node = Mock()
        mock_text_child.dom_node.tag = "text"
        mock_text_child.lines = ["Line 1", "Line 2", "Line 3"]
        mock_text_child.box = Mock()
        mock_text_child.box.x = 10
        mock_text_child.box.y = 20

        layout_node = LayoutNode(b_dom)
        layout_node.children = [mock_text_child]

        mock_renderer = Mock()
        mock_renderer._get_font.return_value = Mock()
        mock_renderer.DEFAULT_FONT_SIZE = 16
        mock_renderer.LINE_HEIGHT = 1.5

        mock_draw = Mock()

        element.render(mock_draw, layout_node, mock_renderer)

        # Should have drawn 3 lines of text
        assert mock_draw.text.call_count == 3

        # Check y positions increase by line height
        calls = mock_draw.text.call_args_list
        expected_line_height = 16 * 1.5  # DEFAULT_FONT_SIZE * LINE_HEIGHT

        assert calls[0][0][0] == (10, 20)  # First line at base position
        assert calls[1][0][0] == (10, 20 + expected_line_height)  # Second line offset
        assert calls[2][0][0] == (
            10,
            20 + 2 * expected_line_height,
        )  # Third line offset
